import functools
from flask import session, redirect, url_for, flash, request, abort, g
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import query_db

def hash_password(password: str) -> str:
    """Generate a secure cryptographic hash for a plaintext password."""
    return generate_password_hash(password, method="scrypt")


def verify_password(stored_hash: str, candidate_password: str) -> bool:
    """Verify candidate password against the stored hash."""
    if not stored_hash or not candidate_password:
        return False
    return check_password_hash(stored_hash, candidate_password)


def login_user(user: dict):
    """Store authenticated user details into Flask session."""
    session.clear()
    session["user_id"] = user["id"]
    session["user_name"] = user["full_name"]
    session["user_email"] = user["email"]
    session["user_role"] = user["role"]
    session["user_avatar"] = user.get("avatar_url") or "/static/images/default-avatar.png"
    session.permanent = True


def logout_user():
    """Clear session data on logout."""
    session.clear()


def get_current_user():
    """Fetch the active user dictionary from database if logged in."""
    user_id = session.get("user_id")
    if not user_id:
        return None
    try:
        user = query_db("SELECT id, full_name, email, phone, role, avatar_url, is_verified, is_active FROM users WHERE id = %s", (user_id,), one=True)
        return user
    except Exception:
        return None


def login_required(view):
    """Decorator to require login before accessing a route."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not session.get("user_id"):
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for("auth.login", next=request.url))
        return view(**kwargs)
    return wrapped_view


def role_required(*allowed_roles):
    """Decorator restricting route access to specified roles ('tenant', 'owner', 'admin')."""
    def decorator(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            user_id = session.get("user_id")
            if not user_id:
                flash("Please sign in to access this page.", "warning")
                return redirect(url_for("auth.login", next=request.url))
            
            user_role = session.get("user_role")
            if user_role not in allowed_roles:
                flash("You do not have permission to view that resource.", "danger")
                if user_role == "owner":
                    return redirect(url_for("owner.dashboard"))
                elif user_role == "admin":
                    return redirect(url_for("admin.dashboard"))
                else:
                    return redirect(url_for("tenant.home"))
            return view(**kwargs)
        return wrapped_view
    return decorator


tenant_required = role_required("tenant")
owner_required = role_required("owner")
admin_required = role_required("admin")

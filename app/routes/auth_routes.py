from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.user import UserModel
from app.services.auth_service import login_user, logout_user, login_required

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        role = session.get("user_role")
        if role == "owner":
            return redirect(url_for("owner.dashboard"))
        elif role == "admin":
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("tenant.home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        next_url = request.args.get("next")

        if not email or not password:
            flash("Please enter both email and password.", "warning")
            return render_template("auth/login.html", email=email)

        user, err = UserModel.authenticate(email, password)
        if err:
            flash(err, "danger")
            return render_template("auth/login.html", email=email)

        login_user(user)
        flash(f"Welcome back, {user['full_name']}!", "success")

        if next_url and next_url.startswith("/"):
            return redirect(next_url)

        if user["role"] == "owner":
            return redirect(url_for("owner.dashboard"))
        elif user["role"] == "admin":
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("tenant.home"))

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("tenant.home"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "tenant").lower()

        if role not in ("tenant", "owner"):
            role = "tenant"

        if not full_name or not email or not phone or not password:
            flash("All fields are required.", "warning")
            return render_template("auth/register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "warning")
            return render_template("auth/register.html")

        if UserModel.get_by_email(email):
            flash("An account with this email already exists. Please sign in.", "warning")
            return redirect(url_for("auth.login"))

        try:
            new_user = UserModel.create(full_name, email, password, phone, role)
            login_user(new_user)
            flash(f"Account created successfully as {role.title()}!", "success")
            if role == "owner":
                return redirect(url_for("owner.dashboard"))
            return redirect(url_for("tenant.home"))
        except Exception as e:
            flash("An error occurred during registration. Please try again.", "danger")
            return render_template("auth/register.html")

    return render_template("auth/register.html")


@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for("tenant.home"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_id = session.get("user_id")
    user = UserModel.get_by_id(user_id)

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()
        if full_name and phone:
            user = UserModel.update_profile(user_id, full_name, phone)
            session["user_name"] = user["full_name"]
            flash("Profile updated successfully.", "success")
        else:
            flash("Name and phone number cannot be blank.", "warning")

    return render_template("auth/profile.html", user=user)

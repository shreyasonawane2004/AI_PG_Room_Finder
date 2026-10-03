from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.user import UserModel
from app.models.property import PropertyModel
from app.models.amenity import AmenityModel
from app.services.auth_service import admin_required

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    all_users = UserModel.get_all(limit=100)
    pending_props = PropertyModel.get_pending_approval()
    all_props = PropertyModel.search({"limit": 100})
    amenities = AmenityModel.get_all()

    total_tenants = sum(1 for u in all_users if u["role"] == "tenant")
    total_owners = sum(1 for u in all_users if u["role"] == "owner")

    return render_template(
        "admin/dashboard.html",
        total_users=len(all_users),
        total_tenants=total_tenants,
        total_owners=total_owners,
        total_properties=len(all_props),
        pending_properties=pending_props,
        amenities=amenities
    )


@admin_bp.route("/listings/verify")
@admin_required
def verify_listings():
    pending_props = PropertyModel.get_pending_approval()
    return render_template("admin/verify_listings.html", pending_properties=pending_props)


@admin_bp.route("/listing/<int:property_id>/action", methods=["POST"])
@admin_required
def verify_action(property_id):
    action = request.form.get("action")  # 'approved' or 'rejected'
    reason = request.form.get("rejection_reason", "")

    if action in ("approved", "rejected"):
        PropertyModel.update_status(property_id, action, reason)
        flash(f"Listing #{property_id} has been {action}.", "success" if action == "approved" else "warning")

    return redirect(url_for("admin.verify_listings"))


@admin_bp.route("/users")
@admin_required
def manage_users():
    users_list = UserModel.get_all(limit=100)
    return render_template("admin/manage_users.html", users=users_list)


@admin_bp.route("/user/<int:user_id>/toggle-status", methods=["POST"])
@admin_required
def toggle_user_status(user_id):
    is_active = request.form.get("is_active") == "1"
    UserModel.toggle_active(user_id, is_active)
    flash(f"User #{user_id} status updated.", "info")
    return redirect(url_for("admin.manage_users"))


@admin_bp.route("/amenities", methods=["GET", "POST"])
@admin_required
def manage_amenities():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "General").strip()
        icon = request.form.get("icon_code", "fa-check").strip()
        if name:
            AmenityModel.create(name, category, icon)
            flash(f"Amenity '{name}' added successfully.", "success")
        return redirect(url_for("admin.manage_amenities"))

    amenities = AmenityModel.get_all()
    return render_template("admin/master_amenities.html", amenities=amenities)

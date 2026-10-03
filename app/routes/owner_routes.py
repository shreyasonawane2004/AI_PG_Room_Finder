from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.property import PropertyModel
from app.models.amenity import AmenityModel
from app.models.booking import BookingModel
from app.services.auth_service import owner_required

owner_bp = Blueprint("owner", __name__)

@owner_bp.route("/dashboard")
@owner_required
def dashboard():
    owner_id = session["user_id"]
    properties = PropertyModel.get_by_owner(owner_id)
    inquiries = BookingModel.get_by_owner(owner_id)

    pending_inquiries = [i for i in inquiries if i["status"] == "pending"]
    total_rooms = sum(p.get("room_count", 0) for p in properties)
    total_available_beds = sum(p.get("total_available_beds", 0) for p in properties)

    return render_template(
        "owner/dashboard.html",
        properties=properties,
        inquiries=inquiries,
        pending_inquiries_count=len(pending_inquiries),
        total_rooms=total_rooms,
        total_available_beds=total_available_beds
    )


@owner_bp.route("/properties")
@owner_required
def properties():
    owner_id = session["user_id"]
    props = PropertyModel.get_by_owner(owner_id)
    return render_template("owner/my_properties.html", properties=props)


@owner_bp.route("/property/new", methods=["GET", "POST"])
@owner_required
def add_property():
    owner_id = session["user_id"]
    amenities = AmenityModel.get_all()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        property_type = request.form.get("property_type", "pg")
        gender_preference = request.form.get("gender_preference", "unisex")
        address_line = request.form.get("address_line", "").strip()
        landmark = request.form.get("landmark", "").strip()
        city = request.form.get("city", "Bangalore").strip()
        state = request.form.get("state", "Karnataka").strip()
        pincode = request.form.get("pincode", "560001").strip()
        latitude = float(request.form.get("latitude", 12.9716))
        longitude = float(request.form.get("longitude", 77.5946))
        notice_period = int(request.form.get("notice_period_days", 30))
        gate_closing_time = request.form.get("gate_closing_time", "No Restriction")
        food_available = bool(request.form.get("food_available"))
        food_type = request.form.get("food_type", "none")
        rules = request.form.get("rules_and_regulations", "").strip()

        if not title or not address_line or not city:
            flash("Please complete all required fields.", "warning")
            return render_template("owner/add_property.html", amenities=amenities)

        prop_data = {
            "title": title,
            "description": description,
            "property_type": property_type,
            "gender_preference": gender_preference,
            "address_line": address_line,
            "landmark": landmark,
            "city": city,
            "state": state,
            "pincode": pincode,
            "latitude": latitude,
            "longitude": longitude,
            "notice_period_days": notice_period,
            "gate_closing_time": gate_closing_time,
            "food_available": food_available,
            "food_type": food_type,
            "rules_and_regulations": rules
        }

        new_prop = PropertyModel.create(prop_data, owner_id)
        prop_id = new_prop["id"]

        # Save selected amenities
        selected_amenities = request.form.getlist("amenities")
        AmenityModel.set_property_amenities(prop_id, selected_amenities)

        # Add initial room configuration
        room_type = request.form.get("initial_room_type", "single")
        total_beds = int(request.form.get("initial_total_beds", 1))
        monthly_rent = float(request.form.get("initial_monthly_rent", 8000.00))
        deposit = float(request.form.get("initial_deposit", 15000.00))
        has_ac = bool(request.form.get("initial_has_ac"))
        has_bath = bool(request.form.get("initial_has_bath"))

        PropertyModel.add_room(prop_id, {
            "room_type": room_type,
            "total_beds": total_beds,
            "available_beds": total_beds,
            "monthly_rent": monthly_rent,
            "security_deposit": deposit,
            "has_ac": has_ac,
            "has_attached_bathroom": has_bath
        })

        # Add image URL
        cover_image = request.form.get("cover_image_url", "").strip()
        if not cover_image:
            cover_image = "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?auto=format&fit=crop&w=800&q=80"
        PropertyModel.add_image(prop_id, cover_image, is_cover=True)

        flash("Listing submitted successfully! It is now pending admin verification.", "success")
        return redirect(url_for("owner.properties"))

    return render_template("owner/add_property.html", amenities=amenities)


@owner_bp.route("/inquiries")
@owner_required
def inquiries():
    owner_id = session["user_id"]
    inquiry_list = BookingModel.get_by_owner(owner_id)
    return render_template("owner/view_inquiries.html", inquiries=inquiry_list)


@owner_bp.route("/inquiry/<int:inquiry_id>/status", methods=["POST"])
@owner_required
def update_inquiry_status(inquiry_id):
    status = request.form.get("status", "pending")
    notes = request.form.get("owner_notes", "")
    BookingModel.update_status(inquiry_id, status, notes)
    flash(f"Inquiry status updated to {status.title()}.", "info")
    return redirect(url_for("owner.inquiries"))

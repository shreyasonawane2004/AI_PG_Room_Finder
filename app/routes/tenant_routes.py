from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.property import PropertyModel
from app.models.amenity import AmenityModel
from app.models.booking import BookingModel
from app.models.review import ReviewModel
from app.models.wishlist import WishlistModel
from app.services.auth_service import login_required, tenant_required
from app.services.ai_search_service import parse_natural_language_query
from app.services.ai_recommender import get_recommendations
from app.services.ai_review_service import summarize_reviews

tenant_bp = Blueprint("tenant", __name__)

@tenant_bp.route("/")
def home():
    featured_properties = PropertyModel.search({"limit": 6})
    recommendations = get_recommendations(limit=4)
    amenities = AmenityModel.get_all()
    return render_template(
        "tenant/home.html",
        featured_properties=featured_properties,
        recommendations=recommendations,
        amenities=amenities
    )


@tenant_bp.route("/search")
def search():
    nl_query = request.args.get("nl_query", "").strip()
    filters = {}
    ai_parsed = None

    if nl_query:
        ai_parsed = parse_natural_language_query(nl_query)
        filters.update(ai_parsed.get("filters", {}))

    # Standard explicit query parameters override or supplement NLP
    if request.args.get("city"):
        filters["city"] = request.args.get("city")
    if request.args.get("gender"):
        filters["gender"] = request.args.get("gender")
    if request.args.get("max_budget"):
        filters["max_budget"] = request.args.get("max_budget")
    if request.args.get("min_budget"):
        filters["min_budget"] = request.args.get("min_budget")
    if request.args.get("sharing"):
        filters["sharing"] = request.args.get("sharing")
    if request.args.get("food"):
        filters["food_available"] = True
    if request.args.get("ac"):
        filters["has_ac"] = True
    if request.args.get("sort"):
        filters["sort"] = request.args.get("sort")

    properties = PropertyModel.search(filters)
    amenities = AmenityModel.get_all()

    return render_template(
        "tenant/search_results.html",
        properties=properties,
        amenities=amenities,
        current_filters=filters,
        nl_query=nl_query,
        ai_parsed=ai_parsed
    )


@tenant_bp.route("/property/<slug>")
def property_detail(slug):
    prop = PropertyModel.get_by_slug(slug)
    if not prop:
        flash("The requested PG accommodation could not be found.", "warning")
        return redirect(url_for("tenant.search"))

    reviews = ReviewModel.get_by_property(prop["id"])
    ai_summary = ReviewModel.get_ai_summary(prop["id"])
    if not ai_summary:
        ai_summary = summarize_reviews(prop["id"])

    user_id = session.get("user_id")
    is_saved = WishlistModel.is_saved(user_id, prop["id"])
    similar_pgs = get_recommendations(current_property_id=prop["id"], limit=3)

    return render_template(
        "tenant/property_detail.html",
        prop=prop,
        reviews=reviews,
        ai_summary=ai_summary,
        is_saved=is_saved,
        similar_pgs=similar_pgs
    )


@tenant_bp.route("/book/<int:property_id>", methods=["POST"])
@login_required
def book_visit(property_id):
    tenant_id = session["user_id"]
    inquiry_type = request.form.get("inquiry_type", "schedule_visit")
    room_id = request.form.get("room_id") or None
    visit_date = request.form.get("visit_date")
    visit_time_slot = request.form.get("visit_time_slot", "Morning (10 AM - 1 PM)")
    message = request.form.get("message", "")

    if not visit_date:
        flash("Please select a preferred visit date.", "warning")
        return redirect(request.referrer or url_for("tenant.home"))

    BookingModel.create(
        tenant_id=tenant_id,
        property_id=property_id,
        room_id=room_id,
        inquiry_type=inquiry_type,
        visit_date=visit_date,
        visit_time_slot=visit_time_slot,
        message=message
    )
    flash("Your visit inquiry has been sent to the property owner! They will contact you shortly.", "success")
    return redirect(url_for("tenant.my_bookings"))


@tenant_bp.route("/my-bookings")
@login_required
def my_bookings():
    tenant_id = session["user_id"]
    bookings = BookingModel.get_by_tenant(tenant_id)
    return render_template("tenant/my_bookings.html", bookings=bookings)


@tenant_bp.route("/wishlist")
@login_required
def wishlist():
    tenant_id = session["user_id"]
    saved_items = WishlistModel.get_by_tenant(tenant_id)
    return render_template("tenant/wishlist.html", saved_items=saved_items)


@tenant_bp.route("/property/<int:property_id>/review", methods=["POST"])
@login_required
def submit_review(property_id):
    tenant_id = session["user_id"]
    rating_overall = int(request.form.get("rating_overall", 5))
    rating_cleanliness = int(request.form.get("rating_cleanliness", 5))
    rating_food = int(request.form.get("rating_food", 5))
    rating_safety = int(request.form.get("rating_safety", 5))
    comment = request.form.get("comment", "").strip()

    if not comment:
        flash("Please provide comments describing your experience.", "warning")
        return redirect(request.referrer or url_for("tenant.home"))

    ReviewModel.create(
        property_id=property_id,
        tenant_id=tenant_id,
        rating_overall=rating_overall,
        rating_cleanliness=rating_cleanliness,
        rating_food=rating_food,
        rating_safety=rating_safety,
        comment=comment
    )
    # Re-run AI summarization with the new review
    summarize_reviews(property_id)
    flash("Thank you for submitting your review!", "success")
    return redirect(request.referrer or url_for("tenant.home"))

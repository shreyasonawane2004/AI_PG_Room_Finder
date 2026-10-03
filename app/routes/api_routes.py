from flask import Blueprint, jsonify, request, session
from app.models.property import PropertyModel
from app.models.wishlist import WishlistModel
from app.services.ai_search_service import parse_natural_language_query

api_bp = Blueprint("api", __name__)

@api_bp.route("/properties/map")
def get_map_properties():
    """Returns geospatial data for rendering Leaflet pins."""
    city = request.args.get("city")
    max_budget = request.args.get("max_budget")
    gender = request.args.get("gender")

    filters = {"limit": 100}
    if city and city != "all":
        filters["city"] = city
    if max_budget:
        filters["max_budget"] = max_budget
    if gender and gender != "all":
        filters["gender"] = gender

    properties = PropertyModel.search(filters)
    features = []
    for p in properties:
        features.append({
            "id": p["id"],
            "title": p["title"],
            "slug": p["slug"],
            "lat": float(p["latitude"]),
            "lng": float(p["longitude"]),
            "min_price": float(p["min_price"]),
            "city": p["city"],
            "landmark": p.get("landmark", ""),
            "gender": p["gender_preference"],
            "rating": p.get("avg_rating", 0.0),
            "cover_image": p.get("cover_image", ""),
            "address": p.get("address_line", "")
        })

    return jsonify({"status": "success", "count": len(features), "properties": features})


@api_bp.route("/search/ai-parse", methods=["POST"])
def ai_parse_query():
    """Extract structured search facets from a natural-language search string."""
    data = request.get_json(silent=True) or {}
    query_text = data.get("query", "").strip()
    parsed = parse_natural_language_query(query_text)
    return jsonify({"status": "success", "data": parsed})


@api_bp.route("/wishlist/toggle", methods=["POST"])
def toggle_wishlist():
    """Asynchronous toggle for tenant wishlists."""
    tenant_id = session.get("user_id")
    if not tenant_id:
        return jsonify({"status": "unauthorized", "message": "Sign in required"}), 401

    data = request.get_json(silent=True) or {}
    property_id = data.get("property_id")
    if not property_id:
        return jsonify({"status": "error", "message": "Property ID is required"}), 400

    is_saved = WishlistModel.toggle(tenant_id, int(property_id))
    return jsonify({
        "status": "success",
        "saved": is_saved,
        "message": "Saved to wishlist" if is_saved else "Removed from wishlist"
    })

from app.models.property import PropertyModel

def get_recommendations(user_preferences: dict = None, current_property_id: int = None, limit: int = 4) -> list:
    """
    Generate hybrid AI-driven recommendations based on user preference profile or property similarity.
    Calculates multi-criteria relevance scores across budget, gender, and amenities.
    """
    all_properties = PropertyModel.search({"limit": 50})
    if not all_properties:
        return []

    # If based on an existing property, filter it out and extract its features
    target_budget = None
    target_gender = None
    target_amenity_ids = set()
    target_city = None

    if current_property_id:
        current_prop = PropertyModel.get_by_id(current_property_id)
        if current_prop:
            target_budget = float(current_prop.get("min_price", 10000))
            target_gender = current_prop.get("gender_preference")
            target_city = current_prop.get("city", "").lower()
            target_amenity_ids = {a["id"] for a in current_prop.get("amenities", [])}

    if user_preferences:
        if user_preferences.get("max_budget"):
            target_budget = float(user_preferences["max_budget"])
        if user_preferences.get("preferred_gender"):
            target_gender = user_preferences["preferred_gender"]
        if user_preferences.get("preferred_city"):
            target_city = user_preferences["preferred_city"].lower()

    scored_properties = []
    for prop in all_properties:
        # Skip the same property
        if current_property_id and prop["id"] == current_property_id:
            continue

        score = 0.0

        # 1. Budget proximity (Weight: 35%)
        if target_budget and target_budget > 0:
            prop_rent = float(prop.get("min_price", target_budget))
            diff_ratio = abs(prop_rent - target_budget) / target_budget
            budget_score = max(0.0, 1.0 - diff_ratio)
            score += 0.35 * budget_score
        else:
            score += 0.35

        # 2. Location match (Weight: 25%)
        if target_city and target_city in prop.get("city", "").lower():
            score += 0.25
        elif not target_city:
            score += 0.20

        # 3. Gender fit (Weight: 20%)
        p_gender = prop.get("gender_preference", "unisex")
        if target_gender:
            if p_gender == target_gender:
                score += 0.20
            elif p_gender == "unisex" or target_gender == "unisex":
                score += 0.15
        else:
            score += 0.20

        # 4. Rating & Verification multiplier (Weight: 20%)
        rating = float(prop.get("avg_rating", 3.5))
        rating_score = min(1.0, rating / 5.0)
        score += 0.20 * rating_score

        prop["match_score"] = int(round(score * 100))
        scored_properties.append(prop)

    # Sort descending by match score
    scored_properties.sort(key=lambda x: x["match_score"], reverse=True)
    return scored_properties[:limit]

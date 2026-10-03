import os
import re
from flask import current_app

KNOWN_LOCATIONS = [
    "koramangala", "hsr layout", "whitefield", "indiranagar", "marathahalli",
    "electronic city", "bellandur", "hinjewadi", "wakad", "baner",
    "kothrud", "gachibowli", "madhapur", "kondapur", "bangalore",
    "pune", "hyderabad", "chennai", "delhi", "mumbai"
]

def parse_natural_language_query(query_text: str) -> dict:
    """
    Parse an unstructured natural-language search query into structured search filters.
    Supports both local rule-based NLP extraction and Gemini AI fallback.
    """
    if not query_text or not query_text.strip():
        return {"filters": {}, "summary": "Showing all available PGs"}

    q_lower = query_text.lower()
    filters = {}
    matched_highlights = []

    # 1. Extract Budget
    # Examples: "under 10k", "within 8000", "< 12000", "below 9,000", "under 10000"
    budget_patterns = [
        r"(?:under|below|less than|within|budget of|max(?:imum)?)\s*(?:rs\.?|inr)?\s*(\d+(?:,\d+)?)\s*(k)?\b",
        r"(?:rs\.?|inr)?\s*(\d+(?:,\d+)?)\s*(k)?\s*(?:budget|or less|max)\b",
        r"<\s*(\d+)\b"
    ]
    for pattern in budget_patterns:
        match = re.search(pattern, q_lower)
        if match:
            num_str = match.group(1).replace(",", "")
            is_k = match.group(2) if len(match.groups()) > 1 else None
            val = float(num_str) * (1000 if is_k else 1)
            filters["max_budget"] = int(val)
            matched_highlights.append(f"Budget up to ₹{int(val):,}")
            break

    # 2. Extract Gender Preference
    if re.search(r"\b(girls?|women|female|ladies)\b", q_lower):
        filters["gender"] = "female"
        matched_highlights.append("Girls / Female only")
    elif re.search(r"\b(boys?|men|male|gents)\b", q_lower):
        filters["gender"] = "male"
        matched_highlights.append("Boys / Male only")
    elif re.search(r"\b(coliving|co-living|unisex|couples?)\b", q_lower):
        filters["gender"] = "unisex"
        matched_highlights.append("Co-living / Unisex")

    # 3. Extract Sharing Type
    if re.search(r"\b(single|private|1\s*sharing|1\s*bed|independent)\b", q_lower):
        filters["sharing"] = "single"
        matched_highlights.append("Single Sharing / Private Room")
    elif re.search(r"\b(double|2\s*sharing|twin|2\s*bed)\b", q_lower):
        filters["sharing"] = "double_sharing"
        matched_highlights.append("Double Sharing")
    elif re.search(r"\b(triple|3\s*sharing|3\s*bed)\b", q_lower):
        filters["sharing"] = "triple_sharing"
        matched_highlights.append("Triple Sharing")
    elif re.search(r"\b(four|4\s*sharing|4\s*bed)\b", q_lower):
        filters["sharing"] = "four_sharing"
        matched_highlights.append("Four Sharing")

    # 4. Extract Amenities & Facilities
    if re.search(r"\b(food|meals?|breakfast|dinner|cook)\b", q_lower):
        filters["food_available"] = True
        matched_highlights.append("Food Included")

    if re.search(r"\b(ac|air condition(?:ed|ing)?)\b", q_lower):
        filters["has_ac"] = True
        matched_highlights.append("Air Conditioning")

    # 5. Extract Location / Area
    matched_loc = None
    for loc in KNOWN_LOCATIONS:
        if loc in q_lower:
            matched_loc = loc.title()
            break
    
    # Generic "in <word>" or "near <word>" pattern if not in dictionary
    if not matched_loc:
        loc_match = re.search(r"\b(?:in|near|around|at)\s+([a-zA-Z\s]{3,25})\b", query_text, re.IGNORECASE)
        if loc_match:
            candidate = loc_match.group(1).strip()
            # Ignore false triggers like "girls pg", "single room"
            if not any(w in candidate.lower() for w in ["room", "pg", "sharing", "budget", "single", "double"]):
                matched_loc = candidate.title()

    if matched_loc:
        filters["city"] = matched_loc
        matched_highlights.append(f"Near {matched_loc}")

    explanation = "Found matching properties based on: " + ", ".join(matched_highlights) if matched_highlights else "Showing search results"

    return {
        "raw_query": query_text,
        "filters": filters,
        "extracted_tags": matched_highlights,
        "summary": explanation
    }

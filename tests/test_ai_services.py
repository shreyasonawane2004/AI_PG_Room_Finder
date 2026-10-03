import pytest
from app.services.ai_search_service import parse_natural_language_query

def test_nlp_query_budget_and_gender():
    query = "Looking for a single room girls PG in Koramangala with food under 12k"
    parsed = parse_natural_language_query(query)

    filters = parsed["filters"]
    assert filters.get("gender") == "female"
    assert filters.get("sharing") == "single"
    assert filters.get("max_budget") == 12000
    assert filters.get("food_available") is True
    assert filters.get("city") == "Koramangala"


def test_nlp_query_boys_ac_pune():
    query = "Hinjewadi Pune boys PG with AC under 8000"
    parsed = parse_natural_language_query(query)

    filters = parsed["filters"]
    assert filters.get("gender") == "male"
    assert filters.get("has_ac") is True
    assert filters.get("max_budget") == 8000
    assert filters.get("city") == "Hinjewadi"


def test_nlp_query_unisex_coliving():
    query = "Whitefield unisex coliving near ITPL"
    parsed = parse_natural_language_query(query)

    filters = parsed["filters"]
    assert filters.get("gender") == "unisex"
    assert filters.get("city") == "Whitefield"

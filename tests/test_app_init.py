import pytest
from app import create_app

def test_app_factory():
    app = create_app("development")
    assert app is not None
    assert app.config["TESTING"] is False

    # Verify all blueprints are registered
    blueprint_names = set(app.blueprints.keys())
    assert "auth" in blueprint_names
    assert "tenant" in blueprint_names
    assert "owner" in blueprint_names
    assert "admin" in blueprint_names
    assert "api" in blueprint_names


def test_cli_help():
    app = create_app("development")
    with app.test_client() as client:
        # Check an unauthenticated redirect or public endpoint
        res = client.get("/auth/login")
        assert res.status_code == 200
        assert b"Welcome Back" in res.data

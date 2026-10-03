import os
from flask import Flask, render_template, session, g
from app.config import config_by_name
from app.database import close_db
from app.services.auth_service import get_current_user

def create_app(config_name=None):
    """Flask Application Factory."""
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    # Ensure uploads directory exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Teardown database connections
    app.teardown_appcontext(close_db)

    # Global context processors for templates
    @app.context_processor
    def inject_user():
        return {
            "current_user": get_current_user(),
            "is_logged_in": bool(session.get("user_id")),
            "user_role": session.get("user_role")
        }

    # Register Blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.tenant_routes import tenant_bp
    from app.routes.owner_routes import owner_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.api_routes import api_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(tenant_bp, url_prefix="")
    app.register_blueprint(owner_bp, url_prefix="/owner")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("components/error.html", code=404, message="Page Not Found"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("components/error.html", code=500, message="An internal server error occurred."), 500

    @app.errorhandler(ConnectionError)
    def db_connection_error(e):
        return render_template(
            "components/error.html",
            code=503,
            message="Database Connection Notice",
            details=str(e),
            action_hint="Please verify your MySQL credentials in the .env file."
        ), 503

    return app

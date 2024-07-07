#!/usr/bin/python3
"""Initializes the engine for the application"""

from datetime import timedelta
from http import HTTPStatus
from os import getenv

from flask import Flask

from api.v1.utils.error_handles.invalid_api_usage import InvalidApiUsage
from api.v1.utils.error_handles.validation_error import ValidationError
from api.v1.views.api_view import api_view
from api.v1.views.auth_view import auth_view
from models import engine
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.register_blueprint(api_view)
app.register_blueprint(auth_view)
app.config["JWT_SECRET_KEY"] = getenv("APP_JWT_SECRET")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

jwt = JWTManager(app)


@jwt.user_identity_loader
def user_identity_lookup(user):
    """Takes what passed to create jwt identity and
    return a seriliazabe version that can be used to lookup
    the user
    Args:
        User: sqlalchemy obj of user
    Returns:
        user's id
    """
    if isinstance(user, str):
        return user
    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    """A callback that lookup a particular user based on
    jwt_data
    Args:
        _jwt_header: contains jwt byte
        jwt_data: contains data contain in jwt
    """
    id = jwt_data["sub"]
    return engine.get("User", id)


@app.teardown_appcontext
def close_session(e):
    """Remove the session object after a requests"""
    engine.close()


@app.errorhandler(InvalidApiUsage)
def invalid_api_usage(e):
    """ Handles all invalid api error"""
    return e.to_dict(), e.status_code


@app.errorhandler(ValidationError)
def validation_error(e):
    """ Handles all validation error"""
    return e.to_dict(), e.status_code


@app.errorhandler(HTTPStatus.NOT_FOUND)
def handle_not_found(e):
    """Handle resource not found for the entire app
    Args:
        e (obj): error obj
    response:
        error: str
    """
    return {"error": "Not found"}, HTTPStatus.NOT_FOUND


if __name__ == '__main__':
    app_port = int(getenv('APP_PORT', 5000))
    app_host = str(getenv('APP_HOST', '0.0.0.0'))
    app_debug = bool(getenv('APP_DEBUG', False))
    print(app_host)
    app.run(port=app_port, host=app_host, debug=app_debug)

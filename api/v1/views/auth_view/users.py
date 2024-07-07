#!/usr/bin/python3

"""Defines endpoints for authentication and management of users"""

from http import HTTPStatus
from typing import Optional

from flask import Response, make_response, request
from flask_jwt_extended import create_access_token, get_current_user
from flask_jwt_extended.view_decorators import jwt_required
from api.v1.utils.error_handles.invalid_api_usage import InvalidApiUsage
from api.v1.views.auth_view import auth_view
from api.v1.utils.schemas.is_valid import isvalid
from sqlalchemy.exc import IntegrityError
from models import engine
from models.users import User
from models.organisations import Organisation


@auth_view.route("/register", methods=["POST"], strict_slashes=False)
@isvalid("create_user.json")
def register_user() -> Response:
    """Register's a user"""
    try:
        user_data = request.get_json()
        new_user = User(**user_data)
        new_user.set_password(user_data["password"])

        access_token = create_access_token(identity=new_user)
        resp = {
            "status": "success",
            "message": "Registration successful",
            "data": {"accessToken": access_token, **new_user.to_dict()}
        }
        users_org = Organisation()
        users_org.set_name(new_user.first_name)
        new_user.organisations.append(users_org)
        new_user.save()

        engine.save()
        return make_response(resp, HTTPStatus.CREATED)
    except (IntegrityError, KeyError):
        raise InvalidApiUsage("Registration unsuccessful")


@auth_view.route("/login", methods=["POST"], strict_slashes=False)
@isvalid("login_user.json")
def login_user() -> Response:
    """Login a user"""
    try:
        user_data = request.get_json()
        user = engine.filter("User", email=user_data["email"])
        if len(user) == 1:
            user = user[0]
        else:
            raise InvalidApiUsage("Authentication failed")
        accessToken = ""
        if (isinstance(user, User) and
                user.check_password(user_data["password"])):
            accessToken = create_access_token(identity=user)
        else:
            raise InvalidApiUsage(
                "Authentication failed",
                status_code=401,
                status_msg="Bad request"
            )
        resp = {
            "status": "success",
            "message": "Login successful",
            "data": {"accessToken": accessToken, **user.to_dict()}
        }

        return make_response(resp, HTTPStatus.OK)
    except InvalidApiUsage:
        raise InvalidApiUsage(
            "Authentication failed",
            status_code=401,
            status_msg="Bad request"
        )


@auth_view.route("/users/<string:id>", strict_slashes=False)
@jwt_required()
def get_user(id) -> Response:
    """a user gets their own record or user record in
    organisations they belong to or created [PROTECTED]
    """
    user = get_current_user()
    resp = {
        "status": "success",
        "message": "you",
        "data": user.to_dict()
    }
    return make_response(resp, HTTPStatus.OK)

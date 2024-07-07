#!/usr/bin/python3

from http import HTTPStatus

from flask import Response, make_response, request
from flask_jwt_extended import get_current_user, jwt_required
from sqlalchemy.exc import IntegrityError

from api.v1.utils.error_handles.invalid_api_usage import InvalidApiUsage
from api.v1.utils.schemas.is_valid import isvalid
from api.v1.views.api_view import api_view
from models import engine
from models.organisations import Organisation
from models.users import User


@api_view.route("/organisations", strict_slashes=False)
@jwt_required()
def get_users_organisations() -> Response:
    """gets all your organisations the user belongs to or created. If a user is
    logged in properly, they can get all their organisations. They should not
    get another user’s organisation [PROTECTED].
    """
    user = get_current_user()
    resp = {
        "status": "success",
        "message": "organisations",
        "data": {
            "organisations": [org.to_dict() for org in user.organisations]
        }
    }
    return make_response(resp, HTTPStatus.OK)


@api_view.route("/organisations/<string:org_id>", strict_slashes=False)
@jwt_required()
def get_organisation_by_id(org_id: str) -> Response:
    """the logged in user gets a single organisation record [PROTECTED]
    Successful response
    """
    user = get_current_user()
    org = engine.get("Organisation", org_id)
    resp = None
    if org not in user.organisations:
        raise InvalidApiUsage("Client Error", status_msg="Bad Request")
    if isinstance(org, Organisation):
        resp = {
            "status": "success",
            "message": "organisation",
            "data": org.to_dict()
        }
    else:
        raise InvalidApiUsage("Client Error", status_msg="Bad Request")

    return make_response(resp, HTTPStatus.OK)


@api_view.route("/organisations", methods=["POST"], strict_slashes=False)
@jwt_required()
@isvalid("create_organisation.json")
def create_organisation() -> Response:
    """a user can create their new organisation [PROTECTED]
    """
    try:
        c_user = get_current_user()
        org_data = request.get_json()
        org = Organisation(**org_data)
        c_user.organisations.append(org)

        resp = {
            "status": "success",
            "message": "Organisation created successfully",
            "data": org.to_dict()
        }
        engine.save()
        return make_response(resp, HTTPStatus.CREATED)
    except IntegrityError:
        raise InvalidApiUsage("Client Error", status_msg="Bad Request")
    except KeyError:
        raise InvalidApiUsage(
            "Server Error",
            status_msg="Internal Server Error",
            status_code=500
        )


@api_view.route(
    "/organisations/<string:org_id>/users",
    methods=["POST"],
    strict_slashes=False
)
@jwt_required()
@isvalid("add_user_to_organisation.json")
def add_user_to_organisation(org_id: str) -> Response:
    """a user can add another user to their organisation [PROTECTED]
    """
    try:
        user_data = request.get_json()
        user = engine.get("User", user_data["userId"])
        org = engine.get("Organisation", org_id)

        if org is None or user is None:
            raise Exception("Client Error")
        if isinstance(org, Organisation) and isinstance(user, User):
            org.users.append(user)
        else:
            raise Exception("Client Error")
        engine.save()
        resp = {
            "status": "success",
            "message": "User added to organisation successfully"
        }
        return make_response(resp, HTTPStatus.OK)
    except IntegrityError:
        raise InvalidApiUsage("Client Error", status_msg="Bad Request")
    except (KeyError, Exception) as e:
        print(e)
        raise InvalidApiUsage(
            "Server Error",
            status_msg="Internal Server Error",
            status_code=500
        )

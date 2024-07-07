#!/venv/bin/python3

"""Decorator to validate a schema with a request object"""
import re
from flask import request
from functools import wraps
from jsonschema import Draft202012Validator
from api.v1.utils.error_handles.validation_error import ValidationError
from api.v1.utils.schemas.resolver import registry


def isvalid(uri_ref):
    """checks if the request object of a particular
    request has the correct decorator
    """
    def decorator_isvalid(f):
        @wraps(f)
        def wrapper_function(*args, **kwargs):
            body = request.get_json()
            v = Draft202012Validator({
                "$ref": uri_ref
            },
                registry=registry,
            )
            errors = sorted(v.iter_errors(body), key=lambda e: e.path)

            if errors:
                error_list = []
                for error in errors:
                    m = re.search(r"(\'.*\')", error.message)
                    field = "general"
                    if m:
                        field = m.group().replace("'", "")
                    error_list.append({
                        "field": field,
                        "message": error.message
                    })

                raise ValidationError(payload=error_list)

            return f(*args, **kwargs)
        return wrapper_function
    return decorator_isvalid

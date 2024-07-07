#!/venv/bin/python3

"""Decorator to validate a schema with a request object"""
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
                "type": "object",
                "additionalProperties": {"$ref": f"{uri_ref}"}
            },
                registry=registry,
            )
            errors = sorted(v.iter_errors({"instance": body}), key=str)
            validation_errors = {}
            if errors:
                for i, error in enumerate(errors):
                    validation_errors[str(i)] = error.message
                raise ValidationError(payload=validation_errors)
            return f(*args, **kwargs)
        return wrapper_function
    return decorator_isvalid

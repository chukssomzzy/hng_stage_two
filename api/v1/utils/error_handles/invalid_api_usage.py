#!./venv/bin/python3

"""Defines class for invalid API usage"""
from http import HTTPStatus
from typing import Dict


class InvalidApiUsage(Exception):
    """InvalidApiUsage class definition"""
    status_code = HTTPStatus.BAD_REQUEST
    payload = None

    def __init__(
        self,
        message,
        status_code=None,
        payload=None,
        status_msg=None
    ) -> None:
        """Initialize InvalidApiUsage"""
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
        self.status_msg = status_msg

    def to_dict(self) -> Dict[str, str]:
        """Get serializable error message"""
        rv = dict(self.payload or ())
        rv["message"] = self.message
        rv["statusCode"] = self.status_code
        rv["status"] = (self.status_code.phrase
                        if not self.status_msg
                        else self.status_msg)
        return rv

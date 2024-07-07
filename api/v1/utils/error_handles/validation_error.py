#!./venv/bin/python3

"""Defines class for validation error"""

from typing import Dict


class ValidationError(Exception):
    """InvalidApiUsage class definition"""
    status_code = 422
    payload = None

    def __init__(
        self,
        payload=None,
        status_code=422
    ) -> None:
        """Initialize InvalidApiUsage"""
        super().__init__()
        self.payload = payload
        self.status_code = status_code

    def to_dict(self) -> Dict[str, str]:
        """Get serializable error message"""
        rv = {}
        rv["errors"] = self.payload
        return rv

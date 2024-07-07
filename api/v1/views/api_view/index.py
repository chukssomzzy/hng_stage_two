#!/usr/bin/python3
"""Get status and stats for the application"""

from api.v1.views.api_view import api_view
from models import engine


@api_view.route('/status', methods=['GET'], strict_slashes=False)
def get_status():
    """Get status of the application"""
    return {"status": "OK"}


@api_view.route('/stats', methods=['GET'], strict_slashes=False)
def get_stats():
    """Get stats of the application"""
    return {
        "users": engine.count("User"),
        "organisations": engine.count("Organisation")
    }

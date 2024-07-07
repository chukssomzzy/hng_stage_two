#!./venv/bin/python3
"""Defines the blueprint for the api view"""

from flask import Blueprint


api_view = Blueprint('api_view', __name__, url_prefix='/api')

from api.v1.views.api_view.index import *
from api.v1.views.api_view.organisation import *

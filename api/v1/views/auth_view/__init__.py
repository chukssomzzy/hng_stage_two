#!./venv/bin/python3
from flask import Blueprint

auth_view = Blueprint('auth_view', __name__, url_prefix='/auth')

from api.v1.views.auth_view.users import *

"""Defines the blueprint for the REST package."""

import functools
from datetime import datetime as dt
from flask import Blueprint
from flask import request, make_response

from app import db
from app.user.models import get_user_by_username
from flask_jwt_extended import get_jwt_identity

bp = Blueprint('rest', __name__)


def json_required(fn):
    """
    A decorator to check for JSON content in the request
    """

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        if request.is_json:
            return fn(*args, **kwargs)
        return make_response({'msg': 'Missing JSON in request'}, 400)

    return wrapper


@bp.after_request
def after_request(response):
    """Execute logic after processing a request."""
    if response.status_code == 500:
        return response
    username = get_jwt_identity()
    if username:
        user = get_user_by_username(username)
        if user:
            user.last_seen = dt.utcnow()
            db.session.add(user)
            db.session.commit()
    return response

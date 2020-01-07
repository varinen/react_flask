"""REST user API."""

import functools
from datetime import datetime as dt
from flask import make_response, request, current_app, jsonify

from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
    get_jwt_claims
)

from app import db
from app.rest import bp
from app.rest.auth import CONST_REALM_MSG
from app.user.models import get_user_by_username, create_user

CONST_UNAUTHORISED = 'Missing permissions'
STATUS_ERROR = 'error'


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


@bp.route('/user', methods=['POST'])
@jwt_required
@json_required
def user_create():
    """Process the route for to create a user."""
    status = 200
    claims = get_jwt_claims()
    if claims['is_admin']:
        username = request.json.get('username', None)
        email = request.json.get('email', None)
        password = request.json.get('password', None)

        try:
            user = create_user(username, email, password)
            result = dict(user_id=user.id)
        except ValueError as ex:
            current_app.logger.error(str(ex))
            status = 500
            result = dict(status=STATUS_ERROR, error_message=str(ex))
        return jsonify(result), status

    return make_response(
        CONST_UNAUTHORISED,
        401,
        {'WWW-Authenticate': f'Basic realm="{CONST_REALM_MSG}"'})

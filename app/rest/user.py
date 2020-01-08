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
from app.user.models import get_user_by_username, create_user, modify_user, \
    User, toggle_admin

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

    return make_response(CONST_UNAUTHORISED, 401)


@bp.route('/user', methods=['PUT'])
@jwt_required
@json_required
def user_modify():
    """Process the route to modify a user."""
    status = 200

    username = request.json.get('username', None)
    modify = request.json.get('modify', {})

    try:
        user_to_edit = get_user_by_username(username)
        if not user_to_edit:
            raise ValueError(f'Username {username} is invalid')

        claims = get_jwt_claims()

        user = get_user_by_username(get_jwt_identity())
        if user.id != user_to_edit.id and not claims['is_admin']:
            return make_response(CONST_UNAUTHORISED, 401)

        updated_user = modify_user(user_to_edit, modify)
        result = dict(user_id=updated_user.id, username=updated_user.username,
                      email=updated_user.email, is_admin=updated_user.is_admin)

    except ValueError as ex:
        current_app.logger.error(str(ex))
        status = 500
        result = dict(status=STATUS_ERROR, error_message=str(ex))

    return jsonify(result), status


@bp.route('/user/admin', methods=['PUT'])
@jwt_required
@json_required
def user_admin():
    """Process the route to toggle the admin status of a user."""
    status = 200

    username = request.json.get('username', None)
    value = bool(request.json.get('value', False))

    try:
        user_to_edit = get_user_by_username(username)
        if not user_to_edit:
            raise ValueError(f'Username {username} is invalid')

        claims = get_jwt_claims()
        user = get_user_by_username(get_jwt_identity())

        if user.id == user_to_edit.id:
            raise ValueError('Cannot edit one\'s own admin status')

        if not claims['is_admin']:
            return make_response(CONST_UNAUTHORISED, 401)

        toggle_admin(user_to_edit, value)
        result = dict(user_id=user_to_edit.id, is_admin=user_to_edit.is_admin)

    except ValueError as ex:
        current_app.logger.error(str(ex))
        status = 500
        result = dict(status=STATUS_ERROR, error_message=str(ex))

    return jsonify(result), status


@bp.route('/user', methods=['GET'])
@jwt_required
@json_required
def user_get():
    """Process the route to get a single user."""
    status = 200

    id_ = request.json.get('id', None)
    username = request.json.get('username', None)

    user = None
    if id_:
        user = User.query.get(id_)
    if not user and username:
        user = get_user_by_username(username)

    if not user:
        status = 404
        result = dict(status=STATUS_ERROR, error_message="User not found")
    else:
        result = dict(user_id=user.id, username=user.username,
                      email=user.email, is_admin=user.is_admin)

    return jsonify(result), status


@bp.route('/user', methods=['DELETE'])
@jwt_required
@json_required
def user_delete():
    """Process the route to delete a user."""
    status = 200

    username = request.json.get('username', None)

    try:
        user_to_delete = get_user_by_username(username)
        if not user_to_delete:
            raise ValueError(f'Username {username} is invalid')

        claims = get_jwt_claims()
        user = get_user_by_username(get_jwt_identity())

        if user.id == user_to_delete.id:
            raise ValueError('Cannot delete one\'s own account')

        if not claims['is_admin']:
            return make_response(CONST_UNAUTHORISED, 401)

        db.session.delete(user_to_delete)
        db.session.commit()

        result = dict(deleted_user_id=user_to_delete.id)

    except ValueError as ex:
        current_app.logger.error(str(ex))
        status = 500
        result = dict(status=STATUS_ERROR, error_message=str(ex))

    return jsonify(result), status
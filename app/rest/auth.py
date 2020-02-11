"""REST Auth API."""

import datetime
from datetime import datetime as dt
from flask_jwt_extended import create_access_token, create_refresh_token, \
    jwt_refresh_token_required, get_jwt_identity

from flask_jwt_extended.config import config as jwt_config

from flask import request, make_response, jsonify

from app import db
from app.rest import bp
from app.user.models import get_user_by_username, get_user_details

CONST_LOGIN_MSG = 'Could not verify'
CONST_REALM_MSG = 'Please login'


@bp.route('/auth/login', methods=['POST'])
def login():
    """Process the login POST request."""
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)

    user = get_user_by_username(username)

    if not user:
        return make_response(CONST_LOGIN_MSG, 401, {
            'WWW-Authenticate': f'Basic realm="{CONST_REALM_MSG}"'})

    if user.check_password(password):
        if user.is_admin:
            claims = {'is_admin': True}
        else:
            claims = {'is_admin': False}

        user.last_seen = dt.utcnow()
        db.session.add(user)
        db.session.commit()

        now = datetime.datetime.now(datetime.timezone.utc)
        access_expires = (now + jwt_config.access_expires).timestamp()
        refresh_expires = (now + jwt_config.refresh_expires).timestamp()

        result = dict(
            access_token=create_access_token(identity=username,
                                             user_claims=claims),
            access_expires=access_expires,
            refresh_expires=refresh_expires,
            refresh_token=create_refresh_token(identity=username)
        )

        return jsonify(dict(result)), 200

    return make_response(
        CONST_LOGIN_MSG,
        401,
        {'WWW-Authenticate': f'Basic realm="{CONST_REALM_MSG}"'})


@bp.route('/auth/refresh', methods=['GET'])
@jwt_refresh_token_required
def refresh():
    """Process the JWT token refresh request."""
    current_user = get_jwt_identity()

    now = datetime.datetime.now(datetime.timezone.utc)
    access_expires = (now + jwt_config.access_expires).timestamp()
    refresh_expires = (now + jwt_config.refresh_expires).timestamp()

    response = {
        'access_token': create_access_token(identity=current_user),
        'access_expires': access_expires,
        'refresh_expires': refresh_expires,
        'refresh_token': create_refresh_token(identity=current_user)

    }
    return jsonify(response), 200

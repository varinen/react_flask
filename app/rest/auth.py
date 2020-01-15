"""REST Auth API."""

import datetime
from datetime import datetime as dt
from flask_jwt_extended import create_access_token, create_refresh_token, \
    jwt_refresh_token_required, get_jwt_identity

from flask import request, make_response, jsonify, current_app
from flask_cors import cross_origin

from app import db
from app.rest import bp
from app.user.models import get_user_by_username

CONST_LOGIN_MSG = 'Could not verify'
CONST_REALM_MSG = 'Please login'


def get_expiry_date(hours: float, now: datetime \
        = datetime.datetime.now(datetime.timezone.utc)) -> datetime:
    """Generate an expiry date using a number of hours."""
    return now + datetime.timedelta(hours=hours)


@bp.route('/auth/login', methods=['POST'])
@cross_origin()
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

        result = dict(
            access_token=create_access_token(identity=username,
                                             user_claims=claims),
            access_expires=get_expiry_date(
                current_app.config[
                    'JWT_ACCESS_TOKEN_EXPIRES_HRS']).timestamp(),
            refresh_expires=get_expiry_date(
                current_app.config[
                    'JWT_REFRESH_TOKEN_EXPIRES_HRS']).timestamp(),
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
    response = {
        'access_token': create_access_token(identity=current_user),
        'access_expires': get_expiry_date(
            current_app.config['JWT_ACCESS_TOKEN_EXPIRES_HRS']).timestamp(),
        'refresh_expires': get_expiry_date(
            current_app.config['JWT_REFRESH_TOKEN_EXPIRES_HRS']).timestamp(),
        'refresh_token': create_refresh_token(identity=current_user)

    }
    return jsonify(response), 200

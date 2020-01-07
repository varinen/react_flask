"""Tests for the Auth module."""

import pytest
import datetime

from flask import url_for
from app.rest.auth import CONST_LOGIN_MSG, get_expiry_date


def test_get_expiry_date():
    now = datetime.datetime.strptime('2019-01-01 00:00:00',
                                     "%Y-%m-%d %H:%M:%S")
    delta = 10
    res = get_expiry_date(delta, now)
    assert res == datetime.datetime.strptime('2019-01-01 10:00:00',
                                             "%Y-%m-%d %H:%M:%S")


def test_auth_login_no_json(app, client):
    """Check application login process fail with a non-json post."""
    with app.test_request_context():
        url = url_for('rest.login')
        response = client.post(url)
        assert response.json.get('msg') == 'Missing JSON in request'


def test_auth_login_invalid_user(app, client):
    """Check application login process fail with an invalid user."""
    with app.test_request_context():
        url = url_for('rest.login')
        response = client.post(url, json=dict(username='invalid'))
        assert response.status_code == 401
        assert CONST_LOGIN_MSG in str(response.data)


@pytest.mark.usefixtures('clean_up_existing_users')
def test_auth_login_valid_user_wrong_pwd(app, client, add_user):
    """Check application login process fail with an invalid password."""
    with app.test_request_context():
        add_user('someuser', 'some@email.com')
        url = url_for('rest.login')
        response = client.post(url, json=dict(username='someuser',
                                              password='invalid'))
        assert response.status_code == 401
        assert CONST_LOGIN_MSG in str(response.data)


@pytest.mark.usefixtures('clean_up_existing_users')
def test_auth_login_valid_user_valid_pwd(app, client, add_user):
    """Check application login success."""
    with app.test_request_context():
        add_user('someuser', 'some@email.com', 'password')
        url = url_for('rest.login')
        response = client.post(url, json=dict(username='someuser',
                                              password='password'))
        assert response.status_code == 200
        assert 'access_token' in response.json
        assert 'refresh_token' in response.json
        assert 'access_expires' in response.json
        assert 'refresh_expires' in response.json


@pytest.mark.usefixtures('clean_up_existing_users')
def test_auth_login_refresh_token(app, client, add_user):
    """Check the use of a JWT refresh tokens."""
    with app.test_request_context():
        add_user('someuser', 'some@email.com', 'password')
        url = url_for('rest.login')
        response = client.post(url, json=dict(username='someuser',
                                              password='password'))
        assert response.status_code == 200
        refresh_token = response.json.get('refresh_token')
        headers = {
            'Authorization': 'Bearer {}'.format(refresh_token)
        }
    with app.test_request_context():
        response = client.get(url_for('rest.refresh'),
                              headers=headers)
        assert response.status_code == 200
        assert 'access_token' in response.json
        assert 'access_expires' in response.json
        assert 'refresh_token' in response.json
        assert 'refresh_expires' in response.json

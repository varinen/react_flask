"""Tests for the user REST module."""

import pytest
from flask import url_for


def test_user_create_no_token(app, client):
    """Check accessing the endpoint without an authentication token."""
    with app.test_request_context():
        response = client.post(url_for('rest.user_create'))
        assert response.status_code == 401


def test_user_create_no_json(app, client, auth_headers):
    """Check accessing the endpoint without a JSON body."""
    with app.test_request_context():
        headers = auth_headers()
        response = client.post(url_for('rest.user_create'), headers=headers)
        assert response.status_code == 400
        assert response.json.get('msg') == 'Missing JSON in request'


def test_user_create_no_admin(app, client, auth_headers):
    """Check accessing the endpoint without is_admin claims."""
    with app.test_request_context():
        user_data = dict(username="new_user")
        headers = auth_headers({'is_admin': False})

        response = client.post(url_for('rest.user_create'), json=user_data,
                               headers=headers)

        assert response.status_code == 401
        assert 'Missing permissions' in str(response.data)


def test_user_create_empty_username(app, client, auth_headers):
    """Check creating a user with an empty username."""
    with app.test_request_context():
        user_data = dict(email="new_user@email.com", password="password")
        headers = auth_headers({'is_admin': True})

        response = client.post(url_for('rest.user_create'), json=user_data,
                               headers=headers)

        assert response.status_code == 500
        assert 'Username cannot be empty' in response.json.get('error_message')


@pytest.mark.usefixtures('clean_up_existing_users')
def test_user_create_user(app, client, auth_headers):
    """Check creating a user."""
    with app.test_request_context():
        user_data = dict(username="new_user", email="new_user@email.com",
                         password="password")
        headers = auth_headers({'is_admin': True})

        response = client.post(url_for('rest.user_create'), json=user_data,
                               headers=headers)

        assert response.status_code == 200
        assert 'user_id' in response.json

"""Tests for the user REST module."""

import pytest
from flask import url_for
from app.user.models import get_user_by_username


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


@pytest.mark.usefixtures('clean_up_existing_users')
def test_user_modify_self(app, client, auth_headers):
    """Check a user modifying himself."""
    with app.test_request_context():
        headers = auth_headers({'is_admin': False})
        original_user = get_user_by_username('default_user')

        user_data = dict(username=original_user.username,
                         modify=dict(username="new_user",
                                     email="new_user@email.com",
                                     password="password"))

        response = client.put(url_for('rest.user_modify'), json=user_data,
                              headers=headers)

        assert response.status_code == 200
        assert response.json.get('user_id') == original_user.id
        assert response.json.get('email') == 'new_user@email.com'
        assert response.json.get('username') == 'new_user'


@pytest.mark.usefixtures('clean_up_existing_users')
def test_user_no_admin_modify_other(app, client, auth_headers, add_user):
    """Check that a non-admin user cannot modify other users."""
    with app.test_request_context():
        # user that edits is 'default_user', his token is in the headers
        headers = auth_headers({'is_admin': False})

        # user that needs to be edited
        user_to_edit = add_user('other_user', 'other_user@email.com')

        user_data = dict(username=user_to_edit.username,
                         modify=dict(username="new_user",
                                     email="new_user@email.com",
                                     password="password"))

        response = client.put(url_for('rest.user_modify'), json=user_data,
                              headers=headers)

        assert response.status_code == 401


@pytest.mark.usefixtures('clean_up_existing_users')
def test_user_admin_modify_other(app, client, auth_headers, add_user):
    """Check that an admin user can modify other users."""
    with app.test_request_context():
        # user that edits is 'default_user', his token is in the headers
        headers = auth_headers({'is_admin': True})

        # user that needs to be edited
        user_to_edit = add_user('other_user', 'other_user@email.com')

        user_data = dict(username=user_to_edit.username,
                         modify=dict(username="new_user",
                                     email="new_user@email.com",
                                     password="password"))

        response = client.put(url_for('rest.user_modify'), json=user_data,
                              headers=headers)

        assert response.status_code == 200
        assert response.json.get('user_id') == user_to_edit.id
        assert response.json.get('email') == 'new_user@email.com'
        assert response.json.get('username') == 'new_user'


@pytest.mark.usefixtures('clean_up_existing_users')
def test_user_admin_modify_non_existing_user(app, client, auth_headers):
    """Check that an admin user cannot modify a non-existing user."""
    with app.test_request_context():
        # user that edits is 'default_user', his token is in the headers
        headers = auth_headers({'is_admin': True})

        user_data = dict(username='non-existing',
                         modify=dict(username="new_user",
                                     email="new_user@email.com",
                                     password="password"))

        response = client.put(url_for('rest.user_modify'), json=user_data,
                              headers=headers)

        assert response.status_code == 500
        assert 'Username non-existing is invalid' in response.json.get(
            'error_message')


@pytest.mark.usefixtures('clean_up_existing_users')
def test_user_admin_modify_user_invalid_email(app, client, auth_headers,
                                              add_user):
    """Check that a user cannot be updated with with an invalid email."""
    with app.test_request_context():
        # user that edits is 'default_user', his token is in the headers
        headers = auth_headers({'is_admin': True})

        # user that needs to be edited
        user_to_edit = add_user('other_user', 'other_user@email.com')

        user_data = dict(username=user_to_edit.username,
                         modify=dict(username="new_username",
                                     email="invalid_email",
                                     password="password"))

        response = client.put(url_for('rest.user_modify'), json=user_data,
                              headers=headers)

        assert response.status_code == 500
        assert 'Email invalid_email is invalid' in response.json.get(
            'error_message')


@pytest.mark.usefixtures('clean_up_existing_users')
def test_user_admin_modify_user_empty_password(app, client, auth_headers,
                                               add_user):
    """Check that a user cannot be updated with with an empty_password."""
    with app.test_request_context():
        # user that edits is 'default_user', his token is in the headers
        headers = auth_headers({'is_admin': True})

        # user that needs to be edited
        user_to_edit = add_user('other_user', 'other_user@email.com')

        user_data = dict(username=user_to_edit.username,
                         modify=dict(username="new_username",
                                     email="new_user@email.com",
                                     password=""))

        response = client.put(url_for('rest.user_modify'), json=user_data,
                              headers=headers)

        assert response.status_code == 500
        assert 'Password cannot be empty' in response.json.get(
            'error_message')


@pytest.mark.usefixtures('clean_up_existing_users')
def test_user_admin_modify_user_invalid_username(app, client, auth_headers,
                                                 add_user):
    """Check that a user cannot be updated with with an invalid username."""
    with app.test_request_context():
        # user that edits is 'default_user', his token is in the headers
        headers = auth_headers({'is_admin': True})

        # user that needs to be edited
        user_to_edit = add_user('other_user', 'other_user@email.com')

        user_data = dict(username=user_to_edit.username,
                         modify=dict(username="",
                                     email="new_user@email.com",
                                     password="password"))

        response = client.put(url_for('rest.user_modify'), json=user_data,
                              headers=headers)

        assert response.status_code == 500
        assert 'Username cannot be empty' in response.json.get(
            'error_message')


@pytest.mark.usefixtures('clean_up_existing_users')
def test_user_admin_modify_admin_self(app, client, auth_headers):
    """Check that an admin user cannot change own admin status."""
    with app.test_request_context():
        headers = auth_headers({'is_admin': True})

        user_data = dict(username='default_user', value=True)

        response = client.put(url_for('rest.user_admin'), json=user_data,
                              headers=headers)

        assert response.status_code == 500
        assert 'Cannot edit one\'s own admin status' in response.json.get(
            'error_message')


@pytest.mark.usefixtures('clean_up_existing_users')
def test_user_no_admin_modify_admin_self(app, client, auth_headers):
    """Check that a non-admin user cannot change own admin status."""
    with app.test_request_context():
        headers = auth_headers({'is_admin': False})

        user_data = dict(username='default_user', value=True)

        response = client.put(url_for('rest.user_admin'), json=user_data,
                              headers=headers)

        assert response.status_code == 500
        assert 'Cannot edit one\'s own admin status' in response.json.get(
            'error_message')


@pytest.mark.usefixtures('clean_up_existing_users')
def test_user_no_admin_modify_admin_other(app, client, auth_headers, add_user):
    """Check that a non-admin user cannot change other's admin status."""
    with app.test_request_context():
        # user that edits is 'default_user', his token is in the headers
        headers = auth_headers({'is_admin': False})

        # user that needs to be edited
        user_to_edit = add_user('other_user', 'other_user@email.com')

        user_data = dict(username=user_to_edit.username, value=True)

        response = client.put(url_for('rest.user_admin'), json=user_data,
                              headers=headers)

        assert response.status_code == 401


@pytest.mark.usefixtures('clean_up_existing_users')
def test_user_admin_modify_admin_non_existing(app, client, auth_headers):
    """Check that an admin can't change a non-existing user's admin rights."""
    with app.test_request_context():
        # user that edits is 'default_user', his token is in the headers
        headers = auth_headers({'is_admin': True})

        user_data = dict(username='other_user', value=True)

        response = client.put(url_for('rest.user_admin'), json=user_data,
                              headers=headers)

        assert response.status_code == 500
        assert 'Username other_user is invalid' in response.json.get(
            'error_message')


@pytest.mark.usefixtures('clean_up_existing_users')
def test_user_admin_modify_admin(app, client, auth_headers, add_user):
    """Check that a admin user can change other's admin status."""
    with app.test_request_context():
        # user that edits is 'default_user', his token is in the headers
        headers = auth_headers({'is_admin': True})

        # user that needs to be edited
        user_to_edit = add_user('other_user', 'other_user@email.com')

        user_data = dict(username=user_to_edit.username, value=True)

        response = client.put(url_for('rest.user_admin'), json=user_data,
                              headers=headers)

        assert response.status_code == 200
        assert response.json.get('user_id') == user_to_edit.id
        assert response.json.get('is_admin')

        user_data = dict(username=user_to_edit.username, value=False)

        response = client.put(url_for('rest.user_admin'), json=user_data,
                              headers=headers)

        assert response.status_code == 200
        assert response.json.get('user_id') == user_to_edit.id
        assert response.json.get('is_admin') == False


@pytest.mark.usefixtures('clean_up_existing_users')
def test_user_get_user_not_found(app, client, auth_headers):
    """Check retrieving non-existing user."""
    with app.test_request_context():
        headers = auth_headers({'is_admin': True})

        user_data = {'username': 'non-existing'}

        response = client.get(url_for('rest.user_get'), json=user_data,
                              headers=headers)

        assert response.status_code == 404
        assert 'User not found' in response.json.get('error_message')


@pytest.mark.usefixtures('clean_up_existing_users')
def test_user_get_user_id(app, client, auth_headers, add_user):
    """Check retrieving a user by id."""
    with app.test_request_context():
        headers = auth_headers({'is_admin': True})

        # user that needs to be retrieved
        user_to_get = add_user('other_user', 'other_user@email.com')

        user_data = {'id': user_to_get.id}

        response = client.get(url_for('rest.user_get'), json=user_data,
                              headers=headers)

        assert response.status_code == 200
        assert user_to_get.id == response.json.get('user_id')
        assert user_to_get.username == response.json.get('username')
        assert user_to_get.email == response.json.get('email')


@pytest.mark.usefixtures('clean_up_existing_users')
def test_user_get_user_username(app, client, auth_headers, add_user):
    """Check retrieving a user by username."""
    with app.test_request_context():
        headers = auth_headers({'is_admin': True})

        # user that needs to be retrieved
        user_to_get = add_user('other_user', 'other_user@email.com')

        user_data = {'username': user_to_get.username}

        response = client.get(url_for('rest.user_get'), json=user_data,
                              headers=headers)

        assert response.status_code == 200
        assert user_to_get.id == response.json.get('user_id')
        assert user_to_get.username == response.json.get('username')
        assert user_to_get.email == response.json.get('email')

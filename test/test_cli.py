"""Testing the  CLI part of the application."""

import pytest


@pytest.mark.usefixtures('clean_up_existing_users')
def test_add_user(app):
    """Test adding user."""
    runner = app.test_cli_runner()
    username = 'user_cli_1'
    result = runner.invoke(app.cli.commands['user'].commands['add'],
                           [username, 'email_cli_1@test.com', 'password'])

    assert f'Added user {username}' in result.output


@pytest.mark.usefixtures('clean_up_existing_users')
def test_modify_username_non_existing(app):
    """Test modifying username on a non-existing user."""
    username = 'cli_mod_username_1'

    runner = app.test_cli_runner()
    result = runner.invoke(
        app.cli.commands['user'].commands['modify-username'],
        [username, 'some_other_name'])

    assert f'Username {username} is invalid' in result.output


@pytest.mark.usefixtures('clean_up_existing_users')
def test_modify_username_invalid(app, add_user):
    """Test modifying username using an invalid value."""
    username = 'cli_mod_username_1'
    invalid_username = ' '
    with app.app_context():
        add_user(username, 'cli_mod_email_1@test.com')

    runner = app.test_cli_runner()
    result = runner.invoke(
        app.cli.commands['user'].commands['modify-username'],
        [username, invalid_username])

    assert f'Username {invalid_username} is invalid' in result.output


@pytest.mark.usefixtures('clean_up_existing_users')
def test_modify_username_valid(app, add_user):
    """Test modifying username using an invalid value."""
    username = 'cli_mod_username_1'
    new_username = 'cli_mod_username_2'
    with app.app_context():
        add_user(username, 'cli_mod_email_1@test.com')

    runner = app.test_cli_runner()
    result = runner.invoke(
        app.cli.commands['user'].commands['modify-username'],
        [username, new_username])

    assert f'Modified username: old = {username}, new = {new_username}' \
           in result.output


@pytest.mark.usefixtures('clean_up_existing_users')
def test_modify_email_non_existing(app):
    """Test modifying the email of a non-existing user."""
    username = 'cli_mod_email_1'
    email = 'cli_mod_email_2@test.com'

    runner = app.test_cli_runner()
    result = runner.invoke(
        app.cli.commands['user'].commands['modify-email'],
        [username, email])

    assert f'Username {username} is invalid' in result.output


@pytest.mark.usefixtures('clean_up_existing_users')
def test_modify_email_invalid(app, add_user):
    """Test modifying the user's email using an invalid email."""
    username = 'cli_mod_email_1'
    email = 'cli_mod_email_2@test.com'
    invalid_email = 'invalid_email'
    with app.app_context():
        add_user(username, email)

    runner = app.test_cli_runner()
    result = runner.invoke(
        app.cli.commands['user'].commands['modify-email'],
        [username, invalid_email])

    assert f'Email {invalid_email} is invalid' in result.output


@pytest.mark.usefixtures('clean_up_existing_users')
def test_modify_email(app, add_user):
    """Test modifying the user's email."""
    username = 'cli_mod_email_1'
    email = 'cli_mod_email_2@test.com'
    valid_email = 'new_cli_mod_username_2@test.com'
    with app.app_context():
        add_user(username, email)

    runner = app.test_cli_runner()

    result = runner.invoke(
        app.cli.commands['user'].commands['modify-email'],
        [username, valid_email])

    assert f'Modified email: old = {email}, new = {valid_email}' \
           in result.output


@pytest.mark.usefixtures('clean_up_existing_users')
def test_modify_password_non_existing(app):
    """Test modifying the password of a non-existing user."""
    username = 'cli_mod_password_1'
    original_password = 'password'

    runner = app.test_cli_runner()
    result = runner.invoke(
        app.cli.commands['user'].commands['modify-password'],
        [username, original_password])

    assert f'Username {username} is invalid' in result.output


@pytest.mark.usefixtures('clean_up_existing_users')
def test_modify_password_invalid(app, add_user):
    """Test modifying the user's password using an empty string."""
    username = 'cli_mod_password_1'
    email = 'cli_mod_password_1@test.com'
    invalid_password = ' '
    original_password = 'password'
    with app.app_context():
        add_user(username, email, original_password)

    runner = app.test_cli_runner()

    result = runner.invoke(
        app.cli.commands['user'].commands['modify-password'],
        [username, invalid_password])

    assert 'Password cannot be empty' in result.output


@pytest.mark.usefixtures('clean_up_existing_users')
def test_modify_password(app, add_user):
    """Test modifying the user's password."""
    username = 'cli_mod_password_1'
    email = 'cli_mod_password_1@test.com'
    original_password = 'password'
    valid_password = 'new_password'
    with app.app_context():
        user = add_user(username, email, original_password)

    runner = app.test_cli_runner()

    result = runner.invoke(
        app.cli.commands['user'].commands['modify-password'],
        [username, valid_password])

    assert f'Modified password for the user {username}' \
           in result.output


@pytest.mark.usefixtures('clean_up_existing_users')
def test_toggle_admin_true(app, add_user):
    """Test granting a user admin rights."""
    username = 'cli_admin_1'
    email = 'cli_admin_1@test.com'
    with app.app_context():
        add_user(username, email)

    runner = app.test_cli_runner()

    result = runner.invoke(
        app.cli.commands['user'].commands['grant-admin'],
        [username])

    assert f'Granted admin rights to the user {username}' \
           in result.output


@pytest.mark.usefixtures('clean_up_existing_users')
def test_toggle_admin_false(app, add_user):
    """Test revoking admin rights from a user."""
    username = 'cli_admin_1'
    email = 'cli_admin_1@test.com'
    with app.app_context():
        add_user(username, email)

    runner = app.test_cli_runner()

    result = runner.invoke(
        app.cli.commands['user'].commands['revoke-admin'],
        [username])

    assert f'Revoked admin rights from the user {username}' \
           in result.output

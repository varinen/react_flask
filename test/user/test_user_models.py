"""Tests for the User models module."""

import pytest
from datetime import datetime as dt
from app import db
from app.user.models import User, get_user_by_username, \
    get_user_by_email, create_user, modify_user, toggle_admin, get_user_details


@pytest.mark.usefixtures('clean_up_existing_users')
def test_user_create(app):
    """Test the creation of a user instance."""
    email = 'email_1@test.com'
    username = 'username_1'
    user = User(email=email, username=username)
    with app.app_context():
        db.session.add(user)
        db.session.commit()

        users = User.query.all()
        assert len(users) == 1
        user = User.query.first()
        assert user.email == email
        assert user.username == username
        assert not user.is_admin
        assert str(user) == '<User {}>'.format(user.id)


def test_user_password_set():
    """Test the set_password function of the class user."""
    user = User()
    assert not user.password_hash
    user.set_password('password')
    assert user.password_hash


def test_user_password_check():
    """Test the check_password function of the class user."""
    user = User()
    user.set_password('password')
    assert user.check_password('password')


@pytest.mark.usefixtures('clean_up_existing_users')
def test_get_user_by_username(app, add_user):
    """Test fetching a user by username."""
    username = 'get_uname'
    with app.app_context():
        user = add_user(username, 'get_uname@test.com')
        user_id = user.id
        non_existing = 'non-existing'

    with app.app_context():
        assert get_user_by_username(non_existing) is None
        found_user = get_user_by_username(username)
        assert found_user.id == user_id


@pytest.mark.usefixtures('clean_up_existing_users')
def test_get_user_by_email(app, add_user):
    """Test fetching a user by email."""
    email = 'get_email@test.com'
    with app.app_context():
        user = add_user('get_email', email)
        user_id = user.id
        non_existing = 'non-existing@test.com'

    with app.app_context():
        assert get_user_by_email(non_existing) is None
        found_user = get_user_by_email(email)
        assert found_user.id == user_id


@pytest.mark.usefixtures('clean_up_existing_users')
def test_create_user(app):
    """Test the creation of a user."""
    email = 'email@test.com'
    username = 'username'
    password = 'password'

    with app.app_context():
        new_user = create_user(username, email, password)
        new_user_id = new_user.id
        assert new_user.username == username

    with app.app_context():
        user = User.query.filter_by(username=username).first()
        assert user is not None
        assert new_user_id == user.id


@pytest.mark.usefixtures('clean_up_existing_users')
def test_create_user_existing_name(app, add_user):
    """Test the creation of a user when the username is taken."""
    email = 'email@test.com'
    username = 'username'
    password = 'password'
    with app.app_context():
        add_user(username, email, password)

    with app.app_context():
        with pytest.raises(ValueError) as err:
            create_user(username, 'some@email.com', password)
        assert str(err.value) == f'Username {username} is taken'


@pytest.mark.usefixtures('clean_up_existing_users')
def test_create_user_existing_email(app, add_user):
    """Test the creation of a user when the email is taken."""
    email = 'email@test.com'
    username = 'username'
    password = 'password'
    with app.app_context():
        add_user(username, email, password)

    with app.app_context():
        with pytest.raises(ValueError) as err:
            create_user('some_other_name', email, password)
        assert str(err.value) == f'Email {email} is taken'


@pytest.mark.usefixtures('clean_up_existing_users')
def test_create_user_email_invalid(app):
    """Test the creation of a user when the email is invalid."""
    email = 'invalid_email'
    username = 'username'
    password = 'password'

    with app.app_context():
        with pytest.raises(ValueError) as err:
            create_user(username, email, password)
        assert str(err.value) == f'Email {email} is invalid'


@pytest.mark.usefixtures('clean_up_existing_users')
def test_create_user_empty_username(app):
    """Test the creation of a user when the username is empty."""
    email = 'email@test.com'
    username = ''
    password = 'password'

    with app.app_context():
        with pytest.raises(ValueError) as err:
            create_user(username, email, password)
        assert str(err.value) == f'Username cannot be empty'


@pytest.mark.usefixtures('clean_up_existing_users')
def test_create_user_empty_email(app):
    """Test the creation of a user when the email is empty."""
    email = ''
    username = 'username'
    password = 'password'

    with app.app_context():
        with pytest.raises(ValueError) as err:
            create_user(username, email, password)
        assert str(err.value) == f'Email cannot be empty'


@pytest.mark.usefixtures('clean_up_existing_users')
def test_create_user_empty_password(app):
    """Test the creation of a user when the password is empty."""
    email = 'email@test.com'
    username = 'username'
    password = ''

    with app.app_context():
        with pytest.raises(ValueError) as err:
            create_user(username, email, password)
        assert str(err.value) == f'Password cannot be empty'


@pytest.mark.usefixtures('clean_up_existing_users')
def test_modify_user_username_empty(app, add_user):
    """Test modifying an exiting user with an empty username."""
    with app.app_context():
        user = add_user('username', 'username@email.com')
        # Update using an empty value
        with pytest.raises(ValueError) as err:
            modify_user(user, {'username': ''})
        assert str(err.value) == f'Username cannot be empty'


@pytest.mark.usefixtures('clean_up_existing_users')
def test_modify_user_username_taken(app, add_user):
    """Test modifying an exiting user with a taken username."""
    with app.app_context():
        user = add_user('username', 'username@email.com')
        other_user = add_user('taken_username', 'taken_username@email.com')

        # Update using a taken username
        with pytest.raises(ValueError) as err:
            modify_user(user, {'username': other_user.username})
        assert str(err.value) == f'Username {other_user.username} is taken'


@pytest.mark.usefixtures('clean_up_existing_users')
def test_modify_user_email_invalid(app, add_user):
    """Test modifying a user with an invalid email."""
    with app.app_context():
        user = add_user('username', 'username@email.com')
        invalid_email = 'invalid_email_format'

        # Update using an invalid email
        with pytest.raises(ValueError) as err:
            modify_user(user, {'email': invalid_email})
        assert str(err.value) == f'Email {invalid_email} is invalid'


@pytest.mark.usefixtures('clean_up_existing_users')
def test_modify_user_email_taken(app, add_user):
    """Test modifying a user with a taken email."""
    with app.app_context():
        user = add_user('username', 'username@email.com')
        other_user = add_user('taken_username', 'taken_username@email.com')

        # Update using a taken email
        with pytest.raises(ValueError) as err:
            modify_user(user, {'email': other_user.email})
        assert str(err.value) == f'Email {other_user.email} is taken'


@pytest.mark.usefixtures('clean_up_existing_users')
def test_modify_user_password_empty(app, add_user):
    """Test modifying a user with an empty password."""
    with app.app_context():
        user = add_user('username', 'username@email.com')

        # Update using an empty password
        with pytest.raises(ValueError) as err:
            modify_user(user, {'password': ''})
        assert str(err.value) == f'Password cannot be empty'


@pytest.mark.usefixtures('clean_up_existing_users')
def test_modify_user_success(app, add_user):
    """Test modifying a user with an empty password."""
    with app.app_context():
        user = add_user('username', 'username@email.com', 'password')

        # Valid update
        user = modify_user(
            user,
            {'username': 'new_username',
             'email': 'new_username@email.com',
             'password': 'new_password'}
        )
        assert user.username == 'new_username'
        assert user.email == 'new_username@email.com'
        assert user.check_password('new_password')


@pytest.mark.usefixtures('clean_up_existing_users')
def test_toggle_admin_true(app, add_user):
    """Test granting a user's admin rights."""
    with app.app_context():
        user = add_user('username', 'username@email.com')

        user = toggle_admin(user, True)
        assert user.is_admin


@pytest.mark.usefixtures('clean_up_existing_users')
def test_toggle_admin_false(app, add_user):
    """Test revoking a user's admin rights."""
    with app.app_context():
        user = add_user('username', 'username@email.com')
        user.is_admin = True

        user = toggle_admin(user, False)
        assert not user.is_admin


def test_user_get_props(app):
    """Test the get_props method of the user model."""
    with app.app_context():
        props = User.get_props()
        assert isinstance(props, list)
        assert len(props) > 0


def test_user_ts_created_at(app):
    """Test the ts_created property of the user model."""
    with app.app_context():
        now = dt.utcnow()
        user = User(created_at=now)
        assert user.ts_created_at == now.timestamp()


def test_user_ts_last_seen(app):
    """Test the ts_last_seen property of the user model."""
    with app.app_context():
        now = dt.utcnow()
        user = User(last_seen=now)
        assert user.ts_last_seen == now.timestamp()


def test_get_user_details(app):
    """Test the get_user_details function."""
    with app.app_context():
        props = User.get_props()
        user = User(username='someuser', email='some_email@email.com',
                    is_admin=True, created_at=dt.utcnow(),
                    last_seen=dt.utcnow())
        details = get_user_details(user)
        for key in details.keys():
            assert key in props

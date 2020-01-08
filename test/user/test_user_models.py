"""Tests for the User models module."""

import math
import pytest
from app import db
from app.user.models import User, get_user_by_username, \
    get_user_by_email, create_user, modify_user, toggle_admin, get_users


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
        assert str(err.value) == f'Username {other_user.username} is invalid'


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
        assert str(err.value) == f'Email {other_user.email} is invalid'


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


@pytest.mark.usefixtures('clean_up_existing_users')
def test_get_users_no_filter_default_sort(app):
    """Test getting a paged list of users without a filter or a sort."""
    with app.app_context():
        users = get_users(1, 5)
        assert users.page == 1
        assert users.per_page == 5
        assert 'ORDER BY users.id ASC' in str(users.query.statement)
        assert users.query.whereclause is None


@pytest.mark.usefixtures('clean_up_existing_users')
def test_get_users_no_filter_sort_username_desc(app):
    """Test getting a paged list of users ordered by username desc."""
    with app.app_context():
        users = get_users(1, 5, [], dict(column='username', dir='desc'))
        assert users.page == 1
        assert users.per_page == 5
        assert 'ORDER BY users.username DESC' in str(users.query.statement)


@pytest.mark.usefixtures('clean_up_existing_users')
def test_get_users_ten_no_filter_sort_username_desc(app, add_ten_users):
    """Test getting a paged list of users without a filter or a sort."""
    with app.app_context():
        add_ten_users()
        users = get_users(1, 3, [], dict(column='id', dir='desc'))
        assert len(users.items) == 3
        assert users.items[0].id == 10
        assert users.has_next
        assert not users.has_prev
        assert users.pages == math.ceil(users.total / users.per_page)


@pytest.mark.usefixtures('clean_up_existing_users')
def test_get_users_ten_filter_id(app, add_ten_users):
    """Test getting a paged list of users filtered by a username."""
    with app.app_context():
        add_ten_users()
        filter = [dict(column='id', type='geq', value=5)]
        users = get_users(2, 3, filter, dict(column='id', dir='desc'))
        assert len(users.items) == 3
        assert not users.has_next
        assert users.has_prev
        assert users.total == 6

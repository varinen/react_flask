"""Configure the test suite."""

import os
import pytest
import tempfile
from flask_migrate import upgrade as _upgrade
from flask_jwt_extended import create_access_token

from app import create_app, db, cli
from config import config_list

from app.user.models import User
from app.note.models import Note


@pytest.fixture(scope='module')
def app():
    """Create and configure a new app instance for each test."""
    # create the app with common test config
    config = config_list['testing']

    db_fd, db_path = tempfile.mkstemp()
    conn_string = 'sqlite:///' + db_path
    config.SQLALCHEMY_DATABASE_URI = conn_string
    # disable CSRF (the regular value is ['POST', 'PUT', 'PATCH']

    app = create_app(config)
    cli.register(app)

    # Make sure that the app in the test context has access to the migrations
    directory = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             os.pardir, 'migrations'))

    # create the database and load test data
    with app.app_context():
        _upgrade(directory)

    yield app

    # close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope='function')
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture(scope='function')
def clean_up_existing_users(app):
    """Clean up existing users."""

    def clean_up_users(app):
        """Clean up users."""
        with app.app_context():
            for user in User.query.all():
                db.session.delete(user)
            db.session.commit()

    return clean_up_users(app)


def _add_user(username, email, password='password') -> User:
    """Add a user and return it or return an existing user."""
    user = User.query.filter_by(username=username).first()
    if user is None:
        user = User.query.filter_by(email=email).first()
    if user is None:
        user = User(username=username, email=email)
    if password is not None:
        user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def add_user():
    """Add a user."""
    return _add_user


@pytest.fixture
def auth_headers():
    """Create a headers list with an access token for a default user."""

    def _auth_headers(claims={'is_admin': False}):
        user = _add_user('default_user', 'default_user@email.com', 'password')
        token = create_access_token(identity=user.username, user_claims=claims)
        headers = {'Authorization': 'Bearer {}'.format(token)}
        return headers

    return _auth_headers


@pytest.fixture
def add_ten_users():
    """Creates a collection of ten user accounts"""

    def add_ten_users():
        users = []
        for i in range(0, 10):
            username = "_".join(['username', str(i)])
            email = "@".join([username, 'email.com'])
            user = _add_user(username, email, 'password')
            users.append(user)
        return users

    return add_ten_users


def _add_note(title='Some title', text='Some text') -> Note:
    """Add a note using a default user account."""
    user = _add_user('some_user', 'some_user@email.com')
    note = Note(created_by=user.id, title=title, text=text)
    db.session.add(note)
    db.session.commit()
    return note


@pytest.fixture
def add_note():
    """Add a note."""
    return _add_note


@pytest.fixture
def add_ten_notes():
    """Creates a collection of ten notes"""

    def add_ten_notes():
        notes = []
        for i in range(0, 10):
            title = '-'.join(['Some title', str(i)])
            text = '-'.join(['Some text', str(i)])
            notes.append(_add_note(title=title, text=text))
        return notes

    return add_ten_notes

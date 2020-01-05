"""Configure the test suite."""

import os
import pytest
import tempfile
from flask_migrate import upgrade as _upgrade

from app import create_app, db
from config import config_list

from app.user.models import User


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


@pytest.fixture
def add_user():
    """Add a user."""

    def _add_user(username, email, password='password', *args, **kwargs):
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

    return _add_user

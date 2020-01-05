"""Tests for the User models module."""

import pytest
from app import db
from app.user.models import User


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

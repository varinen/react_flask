"""Test the utils module."""

import pytest
from app.user.models import User
from app.utils import apply_filter


def test_apply_filter_none(app):
    """Test setting an empty filter."""
    with app.app_context():
        users = User.query
        users = apply_filter(users, User, {})
        assert users.whereclause is None


def test_apply_filter_like(app):
    "Test setting a like type filter."
    with app.app_context():
        users = User.query
        users = apply_filter(users, User,
                             {'field': 'username', 'type': 'like',
                              'value': 'user'})
        assert str(users.whereclause) == 'users.username LIKE :username_1'


def test_apply_filter_equal(app):
    "Test setting an equal type filter."
    with app.app_context():
        users = User.query
        users = apply_filter(users, User,
                             {'field': 'username', 'type': 'eq',
                              'value': 'user'})
        assert str(users.whereclause) == 'users.username = :username_1'


def test_apply_filter_geq(app):
    "Test setting a greater than or equal type filter."
    with app.app_context():
        users = User.query
        users = apply_filter(users, User,
                             {'field': 'id', 'type': 'geq',
                              'value': '1'})
        assert str(users.whereclause) == 'users.id >= :id_1'


def test_apply_filter_leq(app):
    "Test setting a less than or equal type filter."
    with app.app_context():
        users = User.query
        users = apply_filter(users, User,
                             {'field': 'last_seen', 'type': 'leq',
                              'value': 121212121})
        assert str(users.whereclause) == 'users.last_seen <= :last_seen_1'


def test_apply_filter_multiple(app):
    "Test setting multiple filters."
    with app.app_context():
        filters = [{'field': 'id', 'type': 'geq',
                    'value': '1'}, {'field': 'last_seen', 'type': 'leq',
                                    'value': 121212121}]
        users = User.query
        for filter_ in filters:
            users = apply_filter(users, User, filter_)

        assert str(users.whereclause) == \
               'users.id >= :id_1 AND users.last_seen <= :last_seen_1'


@pytest.mark.usefixtures('clean_up_existing_users')
def test_filter_users_eq(app, add_twenty_users):
    """Test the eq type filter on an actual query."""
    with app.app_context():
        add_twenty_users()
        users = User.query
        users = apply_filter(users, User, {'field': 'id', 'type': 'eq',
                                           'value': '2'})
        result = users.all()
        assert len(result) == 1


@pytest.mark.usefixtures('clean_up_existing_users')
def test_filter_users_geq(app, add_twenty_users):
    """Test the geq type filter on an actual query."""
    with app.app_context():
        add_twenty_users()
        users = User.query
        users = apply_filter(users, User, {'field': 'id', 'type': 'geq',
                                           'value': '10'})
        result = users.all()
        assert len(result) == 11


@pytest.mark.usefixtures('clean_up_existing_users')
def test_filter_users_like(app, add_twenty_users):
    """Test the like type filter on an actual query."""
    with app.app_context():
        add_twenty_users()
        users = User.query
        users = apply_filter(users, User, {'field': 'username', 'type': 'like',
                                           'value': '%name_1%'})
        result = users.all()
        assert len(result) == 11

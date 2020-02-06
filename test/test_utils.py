"""Test the utils module."""

import pytest
from datetime import datetime as dt
from app.user.models import User
from app.utils import apply_filter, strip_column_prefix, process_filter_value


def test_strip_column_prefix():
    """Test the column name stripping function."""
    assert strip_column_prefix("ts_some_name") == "some_name"
    assert strip_column_prefix("some_name") == "some_name"
    # only the prefix may be stripped
    assert strip_column_prefix("ts_some_ts_name") == "some_ts_name"
    assert strip_column_prefix("some_ts_name") == "some_ts_name"


def test_process_filter_value():
    """Test the value converting functionality."""
    now = dt.utcnow()
    now_ts = now.timestamp()
    filter_ = {'column': "ts_created_at", 'value': now_ts, type: 'leq'}
    assert process_filter_value(filter_) == now

    filter_ = {'column': "created_at", 'value': now_ts, type: 'leq'}
    assert process_filter_value(filter_) == now_ts


def test_apply_filter_none(app):
    """Test setting an empty filter."""
    with app.app_context():
        users = User.query
        users = apply_filter(users, User, {})
        assert users.whereclause is None


def test_apply_filter_like(app):
    """Test setting a like type filter."""
    with app.app_context():
        users = User.query
        users = apply_filter(users, User,
                             {'column': 'username', 'type': 'like',
                              'value': 'user'})
        assert str(users.whereclause) == 'users.username LIKE :username_1'


def test_apply_filter_equal(app):
    """Test setting an equal type filter."""
    with app.app_context():
        users = User.query
        users = apply_filter(users, User,
                             {'column': 'username', 'type': 'eq',
                              'value': 'user'})
        assert str(users.whereclause) == 'users.username = :username_1'


def test_apply_filter_geq(app):
    """Test setting a greater than or equal type filter."""
    with app.app_context():
        users = User.query
        users = apply_filter(users, User,
                             {'column': 'id', 'type': 'geq',
                              'value': '1'})
        assert str(users.whereclause) == 'users.id >= :id_1'


def test_apply_filter_leq(app):
    """Test setting a less than or equal type filter."""
    with app.app_context():
        users = User.query
        users = apply_filter(users, User,
                             {'column': 'last_seen', 'type': 'leq',
                              'value': 121212121})
        assert str(users.whereclause) == 'users.last_seen <= :last_seen_1'


def test_apply_filter_multiple(app):
    """Test setting multiple filters."""
    with app.app_context():
        filters = [{'column': 'id', 'type': 'geq',
                    'value': '1'}, {'column': 'last_seen', 'type': 'leq',
                                    'value': 121212121}]
        users = User.query
        for filter_ in filters:
            users = apply_filter(users, User, filter_)

        assert str(users.whereclause) == \
               'users.id >= :id_1 AND users.last_seen <= :last_seen_1'


@pytest.mark.usefixtures('clean_up_existing_users')
def test_filter_users_eq(app, add_ten_users):
    """Test the eq type filter on an actual query."""
    with app.app_context():
        add_ten_users()
        users = User.query
        users = apply_filter(users, User, {'column': 'id', 'type': 'eq',
                                           'value': '2'})
        result = users.all()
        assert len(result) == 1


@pytest.mark.usefixtures('clean_up_existing_users')
def test_filter_users_geq(app, add_ten_users):
    """Test the geq type filter on an actual query."""
    with app.app_context():
        add_ten_users()
        users = User.query
        users = apply_filter(users, User, {'column': 'id', 'type': 'geq',
                                           'value': '5'})
        result = users.all()
        assert len(result) == 6


@pytest.mark.usefixtures('clean_up_existing_users')
def test_filter_users_like(app, add_ten_users):
    """Test the like type filter on an actual query."""
    with app.app_context():
        add_ten_users()
        users = User.query
        users = apply_filter(users, User,
                             {'column': 'username', 'type': 'like',
                              'value': '%name_1%'})
        result = users.all()
        assert len(result) == 1

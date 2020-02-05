"""Test the utils module."""

import math
import pytest
from app.user.models import User
from app.note.models import Note
from app.utils import apply_filter, get_entities


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
                             {'column': 'username', 'type': 'like',
                              'value': 'user'})
        assert str(users.whereclause) == 'users.username LIKE :username_1'


def test_apply_filter_equal(app):
    "Test setting an equal type filter."
    with app.app_context():
        users = User.query
        users = apply_filter(users, User,
                             {'column': 'username', 'type': 'eq',
                              'value': 'user'})
        assert str(users.whereclause) == 'users.username = :username_1'


def test_apply_filter_geq(app):
    "Test setting a greater than or equal type filter."
    with app.app_context():
        users = User.query
        users = apply_filter(users, User,
                             {'column': 'id', 'type': 'geq',
                              'value': '1'})
        assert str(users.whereclause) == 'users.id >= :id_1'


def test_apply_filter_leq(app):
    "Test setting a less than or equal type filter."
    with app.app_context():
        users = User.query
        users = apply_filter(users, User,
                             {'column': 'last_seen', 'type': 'leq',
                              'value': 121212121})
        assert str(users.whereclause) == 'users.last_seen <= :last_seen_1'


def test_apply_filter_multiple(app):
    "Test setting multiple filters."
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


@pytest.mark.usefixtures('clean_up_existing_users')
def test_get_entities_user_no_filter_default_sort(app):
    """Test getting a paged list of users without a filter."""
    with app.app_context():
        users = get_entities(User, 1, 5)
        assert users.page == 1
        assert users.per_page == 5
        assert 'ORDER BY users.id ASC' in str(users.query.statement)
        assert users.query.whereclause is None


@pytest.mark.usefixtures('clean_up_existing_users')
def test_get_entities_no_filter_sort_username_desc(app):
    """Test getting a paged list of users ordered by username desc."""
    with app.app_context():
        users = get_entities(User, 1, 5, [],
                             dict(column='username', dir='desc'))
        assert users.page == 1
        assert users.per_page == 5
        assert 'ORDER BY users.username DESC' in str(users.query.statement)


@pytest.mark.usefixtures('clean_up_existing_users')
def test_get_entities_ten_no_filter_sort_username_desc(app, add_ten_users):
    """Test getting a paged list of users without a filter or a sort."""
    with app.app_context():
        add_ten_users()
        users = get_entities(User, 1, 3, [], dict(column='id', dir='desc'))
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
        filters = [dict(column='id', type='geq', value=5)]
        users = get_entities(User, 2, 3, filters,
                             dict(column='id', dir='desc'))
        assert len(users.items) == 3
        assert not users.has_next
        assert users.has_prev
        assert users.total == 6


@pytest.mark.usefixtures('clean_up_existing_users')
def test_get_entities_note_no_filter_default_sort(app):
    """Test getting a paged list of notes without a filter."""
    with app.app_context():
        notes = get_entities(Note, 1, 5)
        assert notes.page == 1
        assert notes.per_page == 5
        assert 'ORDER BY notes.id ASC' in str(notes.query.statement)
        assert notes.query.whereclause is None


@pytest.mark.usefixtures('clean_up_existing_users')
def test_get_entities_invalid_page_default_sort(app, add_ten_users):
    """Test getting a paged list with a correct page when the requested page
    is too high."""
    with app.app_context():
        add_ten_users()
        filters = []
        """Ten users, 3 per page. Max possible page count 4. 
        Call page 5 and receive page 4."""
        users = get_entities(User, 5, 3, filters,
                             dict(column='id', dir='desc'))
        assert len(users.items) == 1
        assert users.page == 4
        assert not users.has_next
        assert users.has_prev
        assert users.total == 10

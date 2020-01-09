"""Test the Note package"""

import json
import pytest
from app import db
from app.user.models import User
from app.note.models import Note, get_current_user_name


@pytest.mark.usefixtures('clean_up_existing_users')
def test_note_create(app, add_user):
    """Test note creation."""
    with app.app_context():
        user = add_user('some_user', 'some_user@email.com')
        note = Note(created_by=user.id)
        db.session.add(note)
        db.session.commit()

        assert note.id > 0
        assert user.id == note.created_by


@pytest.mark.usefixtures('clean_up_existing_users')
def test_note_user_notes_relationships(app, add_user):
    """Test user notes relationship."""
    with app.app_context():
        user = add_user('some_user', 'some_user@email.com')
        note = Note(created_by=user.id)
        db.session.add(note)
        db.session.commit()
        note_id = note.id

        notes = {note.id: note for note in user.get_notes()}
        assert note_id in notes.keys()


@pytest.mark.usefixtures('clean_up_existing_users')
def test_note_user_cascade_delete(app, add_user):
    """Test that user notes are deleted when the user is deleted."""
    with app.app_context():
        user = add_user('some_user', 'some_user@email.com')
        note = Note(created_by=user.id)
        db.session.add(note)
        db.session.commit()
        note_id = note.id
        user_id = user.id

    with app.app_context():
        user_delete = User.query.get(user_id)
        db.session.delete(user_delete)
        db.session.commit()

        note = Note.query.get(note_id)
        assert note is None


@pytest.mark.usefixtures('clean_up_existing_users')
def test_note_author_user_relationships(app, add_user):
    """Test the note's relationship to user."""
    with app.app_context():
        user = add_user('some_user', 'some_user@email.com')
        note = Note(created_by=user.id)
        db.session.add(note)
        db.session.commit()

        assert note.author.id == user.id


def test_note_repr():
    """Test the string representation of a note model."""
    note = Note(id=1, title='Test title')

    assert '<Note Test title - 1>' == str(note)


def test_note_old_data():
    """Test setting and getting the old_data property of the note model."""
    note = Note()

    assert note.old_data is None

    note.old_data = dict(some_data=1)
    assert isinstance(note.old_data, dict)
    assert note.old_data['some_data'] == 1


def test_note_version_list():
    """Test the version list property of the note model."""
    note = Note()
    assert note.version_list == {}

    note.versions = json.dumps({'1': {'text': 'some text'}})
    assert len(note.version_list) == 1
    assert '1' in note.version_list.keys()


def test_note_version_list_non_parsable(app):
    """Test the version_list prop when the versions can't be JSON parsed."""
    with app.app_context():
        note = Note()
        assert note.version_list == {}

        note.versions = 'non-parsable string'
        assert note.version_list == {}


def test_create_version(app):
    """Test creating the new version of a note."""
    with app.app_context():
        note = Note()
        note.version_num = 1
        note.old_data = dict(text='version 1 text')
        note.create_version()
        assert note.version_num == '2'
        assert len(note.version_list) == 1
        assert note.version_list['1']['text'] == 'version 1 text'
        assert 'modified_by' in note.version_list['1'].keys()
        assert 'version_at' in note.version_list['1'].keys()


def test_get_current_user_name():
    """Test getting the current user name."""

    def test_identity():
        return 'test_user'

    def test_identity_none():
        return None

    assert get_current_user_name(test_identity) == 'test_user'
    assert get_current_user_name(test_identity_none) == 'system'


@pytest.mark.usefixtures('clean_up_existing_users')
def test_note_before_commit_listener(app, add_user):
    """Test the note version creation when the note is updated."""
    with app.app_context():
        user = add_user('some_user', 'some_user@email.com')
        note = Note(created_by=user.id, title='version_1_title')
        db.session.add(note)
        db.session.commit()

        note_id = note.id

    with app.app_context():
        note_update = Note.query.get(note_id)
        note_update.title = 'version_2_title'

        assert note_update.version_num == 1
        db.session.add(note_update)
        db.session.commit()

        assert note_update.version_num == 2
        assert len(note_update.version_list) == 1


@pytest.mark.usefixtures('clean_up_existing_users')
def test_note_note_load_listener(app, add_user):
    """Test the note version creation when the note is updated."""
    with app.app_context():
        user = add_user('some_user', 'some_user@email.com')
        note = Note(created_by=user.id, title='version_1_title')
        db.session.add(note)
        db.session.commit()

        note_id = note.id
        assert note.old_data is None

    with app.app_context():
        note_loaded = Note.query.get(note_id)

        assert isinstance(note_loaded.old_data, dict)
        assert len(note_loaded.old_data) > 0

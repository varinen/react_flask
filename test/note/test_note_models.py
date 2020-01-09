"""Test the Note package"""

import pytest
from app import db
from app.user.models import User
from app.note.models import Note


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

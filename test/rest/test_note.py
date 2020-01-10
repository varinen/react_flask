"""Tests for the mote REST module."""

import pytest
from flask import url_for
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.note.models import Note


@pytest.mark.usefixtures('clean_up_existing_users')
def test_user_create_note(app, client, auth_headers):
    """Check creating a note."""
    with app.test_request_context():
        note_data = dict(title='Some title', text='some text')
        headers = auth_headers()

        response = client.post(url_for('rest.note_create'), json=note_data,
                               headers=headers)

        note_id = response.json.get('note_id')
        assert response.status_code == 200
        assert note_id > 0
    with app.app_context():
        note = Note.query.get(note_id)
        assert note.title == 'Some title'
        assert note.text == 'some text'


@pytest.mark.usefixtures('clean_up_existing_users')
def test_user_create_empty_title(app, client, auth_headers):
    """Check creating a note with an empty title."""
    with app.test_request_context():
        note_data = dict(title='', text='some text')
        headers = auth_headers()

        response = client.post(url_for('rest.note_create'), json=note_data,
                               headers=headers)

        assert response.status_code == 500
        assert 'Title can\'t be empty' in response.json.get('error_message')


@pytest.mark.usefixtures('clean_up_existing_users')
def test_lead_post_exception(app, client, auth_headers, monkeypatch):
    """Test handling of a db exception when saving a note."""

    def mock_commit():
        """Monkeypatch the db.session's commit function."""
        raise SQLAlchemyError('some error')

    with app.test_request_context():
        note_data = dict(title='title', text='some text')
        headers = auth_headers()

        monkeypatch.setattr(db.session, 'commit', mock_commit)

        response = client.post(url_for('rest.note_create'), json=note_data,
                               headers=headers)

        assert response.status_code == 500
        assert 'Unable to create the note' in response.json.get(
            'error_message')

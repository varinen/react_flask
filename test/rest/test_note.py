"""Tests for the Note REST module."""

import pytest
from flask import url_for
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.note.models import Note


@pytest.mark.usefixtures('clean_up_existing_users')
def test_note_create(app, client, auth_headers):
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
def test_note_create_empty_title(app, client, auth_headers):
    """Check creating a note with an empty title."""
    with app.test_request_context():
        note_data = dict(title='', text='some text')
        headers = auth_headers()

        response = client.post(url_for('rest.note_create'), json=note_data,
                               headers=headers)

        assert response.status_code == 500
        assert 'Title can\'t be empty' in response.json.get('error_message')


@pytest.mark.usefixtures('clean_up_existing_users')
def test_note_create_exception(app, client, auth_headers, monkeypatch):
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


@pytest.mark.usefixtures('clean_up_existing_users')
def test_note_update(app, client, add_note, auth_headers):
    """Check updating a note."""
    with app.app_context():
        note = add_note('Some title', 'some text')
        note_id = note.id

    with app.test_request_context():
        note_data = dict(id=note_id, title='Some title updated',
                         text='some text updated')

        headers = auth_headers()

        response = client.put(url_for('rest.note_update'), json=note_data,
                              headers=headers)

        note_id = response.json.get('note_id')
        assert response.status_code == 200
        assert note_id > 0
    with app.app_context():
        note = Note.query.get(note_id)
        assert note.title == 'Some title updated'
        assert note.text == 'some text updated'


@pytest.mark.usefixtures('clean_up_existing_users')
def test_note_update_non_existing(app, client, auth_headers):
    """Check updating a non-existing note."""
    with app.test_request_context():
        note_data = dict(id=100000, title='Some title updated',
                         text='some text updated')

        headers = auth_headers()

        response = client.put(url_for('rest.note_update'), json=note_data,
                              headers=headers)

        assert response.status_code == 500
        assert 'Invalid note' in response.json.get('error_message')


@pytest.mark.usefixtures('clean_up_existing_users')
def test_note_update_empty_title(app, client, add_note, auth_headers):
    """Check updating a note with an empty title."""
    with app.app_context():
        note = add_note('Some title', 'some text')
        note_id = note.id

    with app.test_request_context():
        note_data = dict(id=note_id, title='',
                         text='some text updated')

        headers = auth_headers()

        response = client.put(url_for('rest.note_update'), json=note_data,
                              headers=headers)

        assert response.status_code == 500
        assert 'Title can\'t be empty' in response.json.get('error_message')


@pytest.mark.usefixtures('clean_up_existing_users')
def test_note_update_exception(app, client, add_note, auth_headers,
                               monkeypatch):
    """Test handling of a db exception when saving a note."""

    def mock_commit():
        """Monkeypatch the db.session's commit function."""
        raise SQLAlchemyError('some error')

    with app.app_context():
        note = add_note('Some title', 'some text')
        note_id = note.id

    with app.test_request_context():
        note_data = dict(id=note_id, title='Some title',
                         text='some text updated')
        headers = auth_headers()

        monkeypatch.setattr(db.session, 'commit', mock_commit)

        response = client.put(url_for('rest.note_update'), json=note_data,
                              headers=headers)

        assert response.status_code == 500
        assert 'Unable to update the note' in response.json.get(
            'error_message')


@pytest.mark.usefixtures('clean_up_existing_users')
def test_note_delete(app, client, add_note, auth_headers):
    """Check deleting a note."""
    with app.app_context():
        note = add_note('Some title', 'some text')
        note_id = note.id

    with app.test_request_context():
        note_data = dict(id=note_id)

        headers = auth_headers()

        response = client.delete(url_for('rest.note_delete'), json=note_data,
                                 headers=headers)

        note_id = response.json.get('note_id')
        assert response.status_code == 200
        assert note_id > 0
    with app.app_context():
        note = Note.query.get(note_id)
        assert note is None


@pytest.mark.usefixtures('clean_up_existing_users')
def test_note_delete_non_existing(app, client, auth_headers):
    """Check deleting a non-existing note."""
    with app.test_request_context():
        note_data = dict(id=100000)

        headers = auth_headers()

        response = client.delete(url_for('rest.note_delete'), json=note_data,
                                 headers=headers)

        assert response.status_code == 500
        assert 'Invalid note' in response.json.get('error_message')


@pytest.mark.usefixtures('clean_up_existing_users')
def test_note_delete_exception(app, client, add_note, auth_headers,
                               monkeypatch):
    """Test handling of a db exception when deleting a note."""

    def mock_commit():
        """Monkeypatch the db.session's commit function."""
        raise SQLAlchemyError('some error')

    with app.app_context():
        note = add_note('Some title', 'some text')
        note_id = note.id

    with app.test_request_context():
        note_data = dict(id=note_id)
        headers = auth_headers()

        monkeypatch.setattr(db.session, 'commit', mock_commit)

        response = client.delete(url_for('rest.note_delete'), json=note_data,
                                 headers=headers)

        assert response.status_code == 500
        assert 'Unable to delete the note' in response.json.get(
            'error_message')


@pytest.mark.usefixtures('clean_up_existing_users')
def test_note_get_single(app, client, add_note, auth_headers):
    """Check getting a single a note."""
    with app.app_context():
        note = add_note('Some title', 'some text')
        note_id = note.id

    with app.test_request_context():
        note_data = dict(id=note_id)

        headers = auth_headers()

        response = client.get(url_for('rest.note_get'), json=note_data,
                              headers=headers)

        expected_keys = ['id', 'created_by', 'created_at', 'last_modified',
                         'title', 'text', 'version_num', 'version_list']
        assert response.status_code == 200
        for key in expected_keys:
            assert key in response.json


@pytest.mark.usefixtures('clean_up_existing_users')
def test_note_get_non_existing(app, client, auth_headers):
    """Check getting a non-existing note."""
    with app.test_request_context():
        note_data = dict(id=100000)

        headers = auth_headers()

        response = client.get(url_for('rest.note_delete'), json=note_data,
                              headers=headers)

        assert response.status_code == 500
        assert 'Invalid note' in response.json.get('error_message')


@pytest.mark.usefixtures('clean_up_existing_users')
def test_get_notes_no_filter(app, client, auth_headers, add_ten_notes):
    """Test fetching an unfiltered note list."""
    with app.test_request_context():
        headers = auth_headers()
        add_ten_notes()
        req_data = dict(page=2, per_page=3)

        response = client.get(url_for('rest.notes_get'), json=req_data,
                              headers=headers)

        assert response.status_code == 200
        assert response.json.get('has_next')
        assert response.json.get('has_prev')
        assert response.json.get('next_num') == 3
        assert response.json.get('page') == 2
        assert response.json.get('pages') == 4
        assert response.json.get('prev_num') == 1
        assert response.json.get('total') == 10
        assert len(response.json.get('note_list')) == 3


@pytest.mark.usefixtures('clean_up_existing_users')
def test_get_notes_filter_id(app, client, auth_headers, add_ten_notes):
    """Test fetching a paginated list of notes filtered by id."""
    with app.test_request_context():
        headers = auth_headers()
        add_ten_notes()
        # expect to fetch 6 notes in 2 pages
        req_data = dict(page=1, per_page=5,
                        filters=[dict(column='id', type='geq', value=5)])

        response = client.get(url_for('rest.notes_get'), json=req_data,
                              headers=headers)

        assert response.status_code == 200
        assert response.json.get('has_next')
        assert not response.json.get('has_prev')
        assert response.json.get('next_num') == 2
        assert response.json.get('page') == 1
        assert response.json.get('pages') == 2
        assert response.json.get('total') == 6
        assert not response.json.get('prev_num')
        assert len(response.json.get('note_list')) == 5


@pytest.mark.usefixtures('clean_up_existing_users')
def test_get_notes_empty_list(app, client, auth_headers):
    """Test fetching an empty note list."""
    with app.test_request_context():
        headers = auth_headers()

        req_data = dict(page=1, per_page=5,
                        filters=[dict(column='title', type='like',
                                      value='non-existing')])

        response = client.get(url_for('rest.notes_get'), json=req_data,
                              headers=headers)

        assert response.status_code == 200
        assert not response.json.get('has_next')
        assert not response.json.get('has_prev')
        assert not response.json.get('next_num')
        assert response.json.get('page') == 1
        assert response.json.get('pages') == 0
        assert response.json.get('total') == 0
        assert not response.json.get('prev_num')
        assert len(response.json.get('note_list')) == 0

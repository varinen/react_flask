"""REST Note API."""

from flask import request, current_app, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.utils import get_entities
from app.rest import bp
from app.rest.blueprint import json_required
from app.note.models import Note, validate_note, get_note_details
from app.user.models import get_user_by_username

NOTES_PER_PAGE = 10


@bp.route('/note', methods=['POST'])
@jwt_required
@json_required
def note_create():
    """Process the route for to create a note."""
    status = 200

    try:
        user = get_user_by_username(get_jwt_identity())

        title = request.json.get('title')
        text = request.json.get('text')
        validate_note(user, title)
        note = Note(created_by=user.id, title=title, text=text)
        db.session.add(note)
        db.session.commit()

        result = dict(note_id=note.id)
    except ValueError as ex:
        status = 500
        result = dict(error_message=str(ex))
    except Exception as ex:
        current_app.logger.error(str(ex))
        status = 500
        result = dict(error_message='Unable to create the note')

    return jsonify(result), status


@bp.route('/note', methods=['PUT'])
@jwt_required
@json_required
def note_update():
    """Process the route for to update a note."""
    status = 200

    try:
        note_id = request.json.get('id', None)
        note = Note.query.get(note_id)
        if not note:
            raise ValueError('Invalid note')

        title = request.json.get('title')
        text = request.json.get('text')
        validate_note(note.author, title)

        note.title = title
        note.text = text

        db.session.add(note)
        db.session.commit()

        result = dict(note_id=note.id)
    except ValueError as ex:
        status = 500
        result = dict(error_message=str(ex))
    except Exception as ex:
        current_app.logger.error(str(ex))
        status = 500
        result = dict(error_message='Unable to update the note')

    return jsonify(result), status


@bp.route('/note', methods=['DELETE'])
@jwt_required
@json_required
def note_delete():
    """Process the route for to delete a note."""
    status = 200

    try:
        note_id = request.json.get('id', None)
        note = Note.query.get(note_id)
        if not note:
            raise ValueError('Invalid note')

        db.session.delete(note)
        db.session.commit()

        result = dict(note_id=note.id)
    except ValueError as ex:
        status = 500
        result = dict(error_message=str(ex))
    except Exception as ex:
        current_app.logger.error(str(ex))
        status = 500
        result = dict(error_message='Unable to delete the note')

    return jsonify(result), status


@bp.route('/note', methods=['GET', 'OPTIONS'])
@jwt_required
def note_get():
    """Process the route for to get a single note."""
    status = 200

    note_id = request.args.get('id', None)

    try:
        note = Note.query.get(note_id)
        if not note:
            raise ValueError('Invalid note')

        note = Note.query.get(note_id)
        result = get_note_details(note)
    except ValueError as ex:
        status = 500
        result = dict(error_message=str(ex))

    return jsonify(result), status


@bp.route('/notes', methods=['GET'])
@jwt_required
@json_required
def notes_get():
    """Process the route to get multiple notes."""
    page = request.json.get('page', 1)
    per_page = request.json.get('per_page', NOTES_PER_PAGE)
    filters = request.json.get('filters', None)
    order = request.json.get('order', None)

    notes = get_entities(Note, page=page, per_page=per_page, filters=filters,
                         order=order)

    note_list = list(map(lambda x: get_note_details(x), notes.items))

    required_attrs = ['has_next', 'has_prev', 'next_num', 'page', 'pages',
                      'per_page', 'prev_num', 'total']

    result = {attr: getattr(notes, attr) for attr in required_attrs}
    result['note_list'] = note_list

    return jsonify(result), 200

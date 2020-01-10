"""REST Note API."""

from flask import request, current_app, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.rest import bp
from app.rest.blueprint import json_required
from app.note.models import Note, validate_note
from app.user.models import get_user_by_username


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

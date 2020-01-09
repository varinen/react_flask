"""Models for the Note package."""

from typing import Union
import json
from datetime import datetime as dt
from flask_jwt_extended import get_jwt_identity

from flask import current_app
from app import db


class Note(db.Model):
    """Note representation."""

    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'),
                           nullable=False, index=True)

    title = db.Column(db.String(255), index=True, default='Untitled')
    text = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=dt.utcnow)
    last_modified = db.Column(db.DateTime, default=dt.utcnow)

    version_num = db.Column(db.Integer, nullable=False, default=1)
    versions = db.Column(db.Text, nullable=True)

    author = db.relationship('User', backref='author')

    _old_data = None

    def __repr__(self) -> str:
        """Generate a representation of the note model."""
        return f'<Note {self.title} - {self.id}>'

    @property
    def old_data(self) -> Union[dict, None]:
        """Return the old data of the note."""
        if self._old_data:
            return self._old_data
        return None

    @old_data.setter
    def old_data(self, value):
        """Set the old data of the note."""
        for key, item in value.items():
            if isinstance(item, dt):
                value[key] = item.timestamp()
        self._old_data = value

    @property
    def version_list(self) -> dict:
        """Return a dictionary of versions."""
        if self.versions is None:
            old_versions = {}
        else:
            try:
                old_versions = json.loads(self.versions)
            except Exception as ex:
                current_app.logger.error(str(ex))
                old_versions = {}

        return old_versions

    def create_version(self):
        """Create a version by storing the old data."""
        old_versions = self.version_list

        if self.old_data is not None:
            old_versions[self.version_num] = self.old_data
            old_versions[self.version_num][
                'version_at'] = dt.utcnow().timestamp()
            old_versions[self.version_num][
                'modified_by'] = get_current_user_name(get_jwt_identity)
        self.versions = json.dumps(old_versions)
        self.version_num = str(int(self.version_num) + 1)


def note_before_commit_listener(session):
    """Create a version for all updated notes in the session."""
    for updated in list(session.dirty):
        if isinstance(updated, Note):
            updated.create_version()
            updated.modified_at = dt.utcnow()


def note_load_listener(session, instance):
    """Listen to the notes being loaded and save data as old data."""
    if isinstance(instance, Note):
        old_data = dict(
            title=instance.title,
            text=instance.text,
            modified_at=instance.last_modified,
            version_num=instance.version_num
        )
        instance.old_data = old_data


def get_current_user_name(identity):
    """Try to get the current user name."""
    username = identity()
    if not username:
        return 'system'
    return username


db.event.listen(db.session, 'before_commit', note_before_commit_listener)
db.event.listen(db.session, 'loaded_as_persistent', note_load_listener)

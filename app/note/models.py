"""Models for the Note package."""

from datetime import datetime as dt
from app import db


class Note(db.Model):
    """Note representation."""

    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'),
                           nullable=False, index=True)
    modified_by = db.Column(db.Integer, db.ForeignKey('users.id'),
                            nullable=False, index=True)

    title = db.Column(db.String(255), index=True, default='Untitled')
    text = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=dt.utcnow)
    last_modified = db.Column(db.DateTime, default=dt.utcnow)

    version_num = db.Column(db.Integer, nullable=False, default=1)
    versions = db.Column(db.Text, nullable=True)

    def __repr__(self) -> str:
        """Generate a representation of the note model."""
        return f'<Note {self.title} - {self.id}>'
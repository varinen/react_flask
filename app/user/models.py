"""Models for the User package."""

from typing import Union
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
from flask import current_app

from app import db


class User(db.Model):
    """User representation."""

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self) -> str:
        """Generate a representation of the user model."""
        return '<User {}>'.format(self.id)

    def set_password(self, password):
        """Set the user password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password) -> bool:
        """Check the user password."""
        return check_password_hash(self.password_hash, password)

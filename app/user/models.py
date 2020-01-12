"""Models for the User package."""

from typing import Union, List
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
from flask import current_app

from app import db
from app.utils import apply_filter
from app.note.models import Note

USERS_PER_PAGE = 10


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

    notes = db.relationship('Note', backref='notes', cascade="all,delete",
                             lazy='dynamic')

    def __repr__(self) -> str:
        """Generate a representation of the user model."""
        return '<User {}>'.format(self.id)

    def set_password(self, password):
        """Set the user password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password) -> bool:
        """Check the user password."""
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_props() -> list:
        """Return the properties that are available to the API."""
        return ['id', 'username', 'email', 'is_admin', 'ts_created_at',
                'ts_last_seen']

    @property
    def ts_last_seen(self) -> float:
        """Return the timestamp of the last_seen time."""
        return self.last_seen.timestamp()

    @property
    def ts_created_at(self) -> float:
        """Return the timestamp of the created time."""
        return self.created_at.timestamp()

    def get_notes(self) -> List[Note]:
        """Returns a list of notes sorted by creation time."""
        sorted_ = self.notes.order_by(Note.created_at.desc())
        return sorted_.all()


def get_user_by_username(username: str) -> Union[User, None]:
    """Get a user by username.

    :param username: user name
    """
    user = User.query.filter_by(username=username).first()
    return user


def get_user_by_email(email: str) -> Union[User, None]:
    """Get a user by email.

    :param email: email
    """
    user = User.query.filter_by(email=email).first()
    return user


def create_user(username: str, email: str, password: str) -> User:
    """Create a new user.

    :param username: unique user name
    :param email: unique email
    :param password: password of the user
    """
    if not username or not username.strip():
        raise ValueError(f'Username cannot be empty')

    if get_user_by_username(username) is not None:
        raise ValueError(f'Username {username} is taken')

    if not email or not email.strip():
        raise ValueError(f'Email cannot be empty')

    if get_user_by_email(email) is not None:
        raise ValueError(f'Email {email} is taken')

    try:
        validate_email(email)
    except EmailNotValidError as e:
        current_app.logger.error(str(e))
        raise ValueError(f'Email {email} is invalid')

    if not password or not password.strip():
        raise ValueError('Password cannot be empty')

    new_user = User()
    new_user.username = username
    new_user.email = email
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()
    return new_user


def modify_user(user: User, values: dict) -> User:
    """Modify the user."""
    for _property, value in iter(values.items()):
        if not value or not value.strip():
            raise ValueError(f'{_property.capitalize()} cannot be empty')

        if _property == 'username':
            check_user = get_user_by_username(value)
            if not check_user or check_user.id == user.id:
                user.username = value
            else:
                raise ValueError(f'Username {value} is invalid')

        elif _property == 'email':
            try:
                validate_email(value)

            except EmailNotValidError as e:
                current_app.logger.error(str(e))
                raise ValueError(f'Email {value} is invalid')

            check_user = get_user_by_email(value)
            if not check_user or check_user.id == user.id:
                user.email = value
            else:
                raise ValueError(f'Email {value} is invalid')

        elif _property == 'password':
            user.set_password(value)

    db.session.add(user)
    db.session.commit()

    return user


def toggle_admin(user: User, status: bool = False) -> User:
    """Toggle the is_admin status of the user."""
    user.is_admin = bool(status)
    db.session.add(user)
    db.session.commit()
    return user


def get_user_details(user: User) -> dict:
    """Return user details as a dictionary."""
    return {attr: getattr(user, attr) for attr in User.get_props()}

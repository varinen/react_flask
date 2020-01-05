"""A command line interface for the project.

Implements commands required to maintain the application.
"""

import functools
import click
from app.user.models import create_user, modify_user, get_user_by_username, \
    toggle_admin


def check_user(func):
    """Decorate to check the user existence."""

    @functools.wraps(func)
    def wrapper_check_user(*args, **kwargs):
        username = kwargs['username']
        user_ = get_user_by_username(username)
        if not user_:
            return print(f'Username {username} is invalid')
        kwargs['user'] = user_
        return func(*args, **kwargs)

    return wrapper_check_user


def register(app):
    """Register cli commands."""

    @app.cli.group()
    def user():
        """Implement user commands."""
        pass

    @user.command()
    @click.argument('username')
    @click.argument('email')
    @click.argument('password')
    def add(username, email, password):
        """Add a user."""
        user_ = create_user(username, email, password)
        print(f'Added user {user_.username}')

    @user.command()
    @click.argument('username')
    @click.argument('new_value')
    @check_user
    def modify_username(username: str, new_value: str, **kwargs):
        """Modify a user's username."""
        try:
            user_ = kwargs['user']
            user_ = modify_user(user_, {'username': new_value})
            print(
                f'Modified username: old = {username}, new = {user_.username}')
        except ValueError as err:
            print(str(err))

    @user.command()
    @click.argument('username')
    @click.argument('email')
    @check_user
    def modify_email(username: str, email: str, **kwargs):
        """Modify a user's email."""
        try:
            user_ = kwargs['user']
            old_email = user_.email
            user_ = modify_user(user_, {'email': email})
            print(
                f'Modified email: old = {old_email}, new = {user_.email}')
        except ValueError as err:
            print(str(err))

    @user.command()
    @click.argument('username')
    @click.argument('password')
    @check_user
    def modify_password(username: str, password: str, **kwargs):
        """Modify a user's password."""
        try:
            user_ = kwargs['user']
            modify_user(user_, {'password': password})
            print(
                f'Modified password for the user {username}')
        except ValueError as err:
            print(str(err))

    @user.command()
    @click.argument('username')
    @click.argument('password')
    @check_user
    def modify_password(username: str, password: str, **kwargs):
        """Modify a user's password."""
        try:
            user_ = kwargs['user']
            modify_user(user_, {'password': password})
            print(
                f'Modified password for the user {username}')
        except ValueError as err:
            print(str(err))

    @user.command()
    @click.argument('username')
    @click.argument('password')
    @check_user
    def grant_admin(username: str, **kwargs):
        """Grant admin rights to a user."""
        try:
            user_ = kwargs['user']
            toggle_admin(user_, True)
            print(
                f'Granted admin rights to the user {username}')
        except ValueError as err:
            print(str(err))

    @user.command()
    @click.argument('username')
    @click.argument('password')
    @check_user
    def revoke_admin(username: str, **kwargs):
        """Revoke admin rights from a user."""
        try:
            user_ = kwargs['user']
            toggle_admin(user_, False)
            print(
                f'Revoked admin rights from the user {username}')
        except ValueError as err:
            print(str(err))

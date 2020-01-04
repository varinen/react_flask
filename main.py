"""React-Flask main script.

Implements the configuration related objects.
:copyright: © 2020 by the DivisionLab (haftungsbeschränkt).
"""
from app import create_app
from app.user.models import User

app = create_app()
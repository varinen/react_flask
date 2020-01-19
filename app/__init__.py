"""React-Flask.

A web application using Flask API to be consumed by a React client
"""

import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from config import config_list

__version__ = "0.1.dev"

env_ = os.environ.get('RF_ENVIRONMENT', 'development')

if env_ in config_list:
    config_val = config_list[env_]
else:
    raise EnvironmentError('Cannot find environment config')

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_class: object = config_val):
    """Create and configure the instance of the application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)

    from app.rest import bp as rest_bp
    app.register_blueprint(rest_bp)

    # Set up file logging
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/react-flask.log',
                                       maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('React-Flask startup')

    @app.route('/')
    def index():
        """Render a simple ping message."""
        return 'Ping!'

    return app

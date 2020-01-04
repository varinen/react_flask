"""React-Flask Config file.

Implements the configuration related objects.
"""
import os
from dotenv import load_dotenv

project_dir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(project_dir, '.env'))


class Config(object):
    """Loads configuration values from the environment
    or uses development values."""

    DEBUG = False
    TESTING = False

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'development secret'

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URI'
    ) or 'mysql+pymysql://dbadmin:password@localhost/react_flask'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SITE_NAME = 'React-Flask'


class DevelopmentConfig(Config):
    """Development configuration overrides."""
    DEBUG = True


class TestingConfig(Config):
    """Testing configuration overrides."""
    TESTING = True


class ProductionConfig(Config):
    """Production configuration overrides."""
    pass


config_list = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

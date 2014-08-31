# -*- coding: utf-8 -*-
import os

os_env = os.environ

class Config(object):
    SECRET_KEY = os_env['FANTACALCIO_SECRET']  # TODO: Change me
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    BCRYPT_LOG_ROUNDS = 13
    ASSETS_DEBUG = False
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
    USE_MANTRA = False
    STARTING_MONEY = 500
    P_LIMIT = 3
    D_LIMIT = 8
    C_LIMIT = 8
    A_LIMIT = 6
    APP_FOLDER = os.path.dirname(os.path.abspath(__file__))
    AVATAR_UPLOAD_FOLDER = 'static/images'

class ProdConfig(Config):
    """Production configuration."""
    ENV = 'prod'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os_env['DATABASE_URL']
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar


class DevConfig(Config):
    """Development configuration."""
    ENV = 'dev'
    DEBUG = True
    DB_NAME = 'dev.db'
    # Put the db file in project root
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/fantacalcio'
    DEBUG_TB_ENABLED = True
    ASSETS_DEBUG = True  # Don't bundle/minify static assets
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.


class TestConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    BCRYPT_LOG_ROUNDS = 1  # For faster tests
    WTF_CSRF_ENABLED = False  # Allows form testing

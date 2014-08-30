# -*- coding: utf-8 -*-
import datetime as dt
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy import ForeignKey, Integer
from sqlalchemy_imageattach.entity import Image, image_attachment
from sqlalchemy.ext.declarative import declarative_base
from flask.ext.login import UserMixin
from flask import current_app
import os
from fantacalcio.settings import Config
#from fantacalcio.players.models import Player
from fantacalcio.extensions import bcrypt
from fantacalcio.database import (
    Column,
    db,
    Model,
    ReferenceCol,
    relationship,
    SurrogatePK,
)

Base = declarative_base()

class Role(SurrogatePK, Model):
    __tablename__ = 'roles'
    name = Column(db.String(80), unique=True, nullable=False)
    user_id = ReferenceCol('users', nullable=True)
    user = relationship('User', backref='roles')

    def __init__(self, name, **kwargs):
        db.Model.__init__(self, name=name, **kwargs)

    def __repr__(self):
        return '<Role({name})>'.format(name=self.name)

class User(UserMixin, SurrogatePK, Model):

    __tablename__ = 'users'
    username = Column(db.String(80), unique=True, nullable=False)
    picture = Column(db.String(80), unique=True)
    #: The hashed password
    password = Column(db.String(128), nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    first_name = Column(db.String(30), nullable=True)
    last_name = Column(db.String(30), nullable=True)
    active = Column(db.Boolean(), default=False)
    is_admin = Column(db.Boolean(), default=False)
    auction_budget = Column(db.Integer, nullable=True, default=Config.STARTING_MONEY)
    players = db.relationship('Player', backref = 'player', lazy = 'dynamic')

    def __init__(self, username, password=None, **kwargs):
        db.Model.__init__(self, username=username, **kwargs)
        if password:
            self.set_password(password)
        else:
            self.password = None

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        return bcrypt.check_password_hash(self.password, value)

    @property
    def full_name(self):
        return "{0} {1}".format(self.first_name, self.last_name)

    def __repr__(self):
        return '<User({username!r})>'.format(username=self.username)

    def avatar_url(self):
        if not self.picture:
            return ''
        avatar_path = current_app.config['AVATAR_UPLOAD_FOLDER']
        return os.path.join(avatar_path, self.picture)

    def to_json(self):
        return {'id': self.id,
                'username': self.username,
                'avatar': self.avatar_url(),
                'first_name': self.first_name,
                'last_name': self.last_name,
                'auction_budget': self.auction_budget}

#
# class UserPicture(Model, Image):
#     """User picture model."""
#
#     user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
#     user = relationship('User', backref='user_picture')
#     __tablename__ = 'user_picture'

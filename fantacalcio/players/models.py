# -*- coding: utf-8 -*-
import datetime as dt
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy import ForeignKey
from flask.ext.login import UserMixin
from fantacalcio.user.models import User
from fantacalcio.settings import Config
from fantacalcio.extensions import bcrypt
from fantacalcio.database import (
    Column,
    db,
    Model,
    ReferenceCol,
    relationship,
    SurrogatePK,
)

#FANTACALCIO
class Player(SurrogatePK, Model):

    __tablename__ = 'players'

    name = Column(db.String(80), unique=True, nullable=False)
    team = Column(db.String(80), nullable=False)
    role = Column(db.String(5), nullable=False)
    original_price = Column(db.Integer, nullable=True)
    auction_price = Column(db.Integer, default=0)
    extracted = Column(db.Boolean(), default=False)
    currently_selected = Column(db.Boolean(), default=False)
    fantacalcio_team = db.Column(db.String(80), db.ForeignKey('users.username'))

    def __init__(self, name, team, role, **kwargs):
        db.Model.__init__(self, name=name, team=team, role=role, **kwargs)

    def __repr__(self):
        return '<Player({name!r})>'.format(name=self.name)

    def to_json(self):
        return {'id': self.id,
                'name': self.name,
                'team': self.team,
                'role': self.role,
                'original_price': self.original_price,
                'auction_price': self.auction_price,
                'extracted': self.extracted,
                'currently_selected': self.currently_selected,
                'fantacalcio_team': self.fantacalcio_team}

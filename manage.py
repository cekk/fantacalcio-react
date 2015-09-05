#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import os
import sys
import subprocess
from flask.ext.script import Manager, Shell, Server, Command, Option
from flask.ext.migrate import MigrateCommand

from fantacalcio.app import create_app
from fantacalcio.user.models import User
from fantacalcio.players.models import Player
from fantacalcio.settings import DevConfig, ProdConfig
from fantacalcio.database import db
from fantacalcio.settings import Config

if os.environ.get("FANTACALCIO_ENV") == 'prod':
    app = create_app(ProdConfig)
else:
    app = create_app(DevConfig)

manager = Manager(app)
TEST_CMD = "py.test tests"

def _make_context():
    """Return context dict for a shell session so you can access
    app, db, and the User model by default.
    """
    return {'app': app, 'db': db, 'User': User, 'Player': Player}

@manager.command
def test():
    """Run the tests."""
    import pytest
    exit_code = pytest.main(['tests', '--verbose'])
    return exit_code

@manager.command
def reset_users():
    """ reset users """
    for user in User.query.all():
        user.players = []
        user.auction_budget = Config.STARTING_MONEY
        db.session.add(user)
        db.session.commit()
        print "%s reset" % user.username

@manager.command
def set_admin(userid):
    """ Set a given user as admin """
    user = User.query.filter_by(username=userid).first()
    if not user:
        print "Utente %s non trovato nel db" % (userid)
        return
    user.is_admin = True
    db.session.add(user)
    db.session.commit()
    print "%s impostato come admin" % user.username


@manager.command
def reset_players():
    """ reset users """
    for i, player in enumerate(Player.query.all()):
        player.auction_price = 0
        player.extracted = False
        player.currently_selected = False
        db.session.add(player)
        db.session.commit()
        print "%s) Reset %s" % (i, player.name)

manager.add_command('runserver', Server(host="0.0.0.0"))
manager.add_command('shell', Shell(make_context=_make_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()

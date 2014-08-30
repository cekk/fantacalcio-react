#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import os
import sys
import subprocess
from flask.ext.script import Manager, Shell, Server
from flask.ext.migrate import MigrateCommand

from fantacalcio.app import create_app
from fantacalcio.user.models import User
from fantacalcio.players.models import Player
from fantacalcio.settings import DevConfig, ProdConfig
from fantacalcio.database import db

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
def populatedb():
    """ populate db """
    with open("/Users/cekk/Desktop/quotazioni.csv", 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for i, row in enumerate(spamreader):
            if i == 0:
                continue
            player = Player(name=row[3],
                            team=row[4],
                            role=row[1],
                            mantra_role=row[2],
                            original_price=row[5])
            db.session.add(player)
            db.session.commit()
            print "%s) Added %s to db" % (i, row[3])

manager.add_command('server', Server(host="0.0.0.0"))
manager.add_command('shell', Shell(make_context=_make_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()

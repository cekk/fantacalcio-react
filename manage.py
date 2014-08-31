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

if os.environ.get("FANTACALCIO_ENV") == 'prod':
    app = create_app(ProdConfig)
else:
    app = create_app(DevConfig)

manager = Manager(app)
TEST_CMD = "py.test tests"

from gunicorn.app.base import Application

class GunicornServer(Command):

    description = 'Run the app within Gunicorn'

    def __init__(self, host='127.0.0.1', port=8000, workers=6):

        self.port = port
        self.host = host
        self.workers = workers

    def get_options(self):
        return (
            Option('-t', '--host',
                   dest='host',
                   default=self.host),

            Option('-p', '--port',
                   dest='port',
                   type=int,
                   default=self.port),

            Option('-w', '--workers',
                   dest='workers',
                   type=int,
                   default=self.workers),
        )

    def handle(self, app, *args, **kwargs):

        host = kwargs['host']
        port = kwargs['port']
        workers = kwargs['workers']

        def remove_non_gunicorn_command_line_args():
            import sys
            args_to_remove = ['--port','-p']
            def args_filter(name_or_value):
                keep = not args_to_remove.count(name_or_value)
                if keep:
                    previous = sys.argv[sys.argv.index(name_or_value) - 1]
                    keep = not args_to_remove.count(previous)
                return keep
            sys.argv = filter(args_filter, sys.argv)

        remove_non_gunicorn_command_line_args()

        from gunicorn import version_info
        if version_info < (0, 9, 0):
            from gunicorn.arbiter import Arbiter
            from gunicorn.config import Config
            arbiter = Arbiter(Config({'bind': "%s:%d" % (host, int(port)),'workers': workers}), app)
            arbiter.run()
        else:
            class FlaskApplication(Application):
                def init(self, parser, opts, args):
                    return {
                        'bind': '{0}:{1}'.format(host, port),
                        'workers': workers
                    }

                def load(self):
                    return app

            FlaskApplication().run()

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
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for i, row in enumerate(csvreader):
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

@manager.command
def reset_users():
    """ reset users """
    for user in User.query.all():
        user.players = []
        user.auction_budget = 500
        db.session.add(user)
        db.session.commit()
        print "%s reset" % user.username

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

manager.add_command('server', Server(host="0.0.0.0"))
manager.add_command('shell', Shell(make_context=_make_context))
manager.add_command('db', MigrateCommand)
manager.add_command('gunicorn', GunicornServer())

if __name__ == '__main__':
    manager.run()

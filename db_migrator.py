# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from app import db, app
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand


migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()

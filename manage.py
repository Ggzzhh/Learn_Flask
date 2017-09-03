#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
from app import create_app, db
from app.models import User, Role
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

@manager.shell
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)
manager.add_command('db', MigrateCommand)

if __name__ == "__main__":
    manager.run()
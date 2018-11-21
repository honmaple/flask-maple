#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: main.py
# Author: jianglin
# Email: mail@honmaple.com
# Created: 2017-12-05 11:48:53 (CST)
# Last Update: Wednesday 2018-11-21 11:31:01 (CST)
#          By:
# Description:
# **************************************************************************
import sys
sys.path.append('..')

from flask import Flask, current_app
from flask.cli import FlaskGroup, run_command
from flask_maple.models import db
from flask_maple.models.permission import GroupMixin as PermGroupMixin
from flask_maple.models.permission import UserMixin as PermUserMixin
from flask_maple.models.permission import UserPermissionMixin, GroupPermissionMixin
from flask_maple.auth.models import GroupMixin, UserMixin
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from code import interact
import os


class User(PermUserMixin, UserMixin, db.Model):
    pass


class UserPermission(UserPermissionMixin, db.Model):
    pass


class Group(PermGroupMixin, GroupMixin, db.Model):
    pass


class GroupPermission(GroupPermissionMixin, db.Model):
    pass


class config:
    DEBUG = True
    SECRET_KEY = 'asdadasd'
    SECRET_KEY_SALT = 'asdasdads'
    TEMPLATES_AUTO_RELOAD = True

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:password@localhost/blog'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'

    BABEL_TRANSLATION_DIRECTORIES = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), os.pardir, 'flask_maple',
            'translations'))


app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)

admin = Admin(name='devops', template_mode='bootstrap3')
for model in [User, Group]:
    admin.add_view(ModelView(model, db.session, category='user'))
admin.init_app(app)

cli = FlaskGroup(add_default_commands=False, create_app=lambda r: app)
cli.add_command(run_command)


@cli.command('shell', short_help='Starts an interactive shell.')
def shell_command():
    ctx = current_app.make_shell_context()
    interact(local=ctx)


@cli.command()
def runserver():
    app.run()


@cli.command()
def initdb():
    """
    Drops and re-creates the SQL schema
    """
    db.drop_all()
    db.configure_mappers()
    db.create_all()
    db.session.commit()


if __name__ == '__main__':
    if len(sys.argv) == 1:
        app.run()
    else:
        cli.main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: main.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-12-05 11:48:53 (CST)
# Last Update:星期五 2017-12-22 17:30:29 (CST)
#          By:
# Description:
# **************************************************************************
import sys
sys.path.append('..')
from flask_script import Manager
from flask import Flask
from flask_maple.models import db
from flask_maple.views import QuickApi
from flask_maple.auth.models import UserMixin
from flask_maple.auth.models import GroupMixin
from flask_maple.permission.models import PermissionMixin
from flask_admin import Admin
from flask_wtf import Form
from flask_admin.contrib.sqla import ModelView


class User(UserMixin, db.Model):
    pass


class Group(GroupMixin, db.Model):
    pass


class Permission(PermissionMixin, db.Model):
    pass


class config:
    DEBUG = True
    SECRET_KEY = 'asdadasd'
    SECRET_KEY_SALT = 'asdasdads'
    TEMPLATES_AUTO_RELOAD = True

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:password@localhost/blog'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'


app = Flask(__name__)
app.config.from_object(config)
api = QuickApi(app)
manager = Manager(app)
db.init_app(app)
api.create_api(User)

admin = Admin(name='devops', template_mode='bootstrap3')
for model in [User, Group, Permission]:
    admin.add_view(ModelView(model, db.session, category='user'))
admin.init_app(app)


@manager.command
def runserver():
    return app.run(port=8000)


@manager.command
def init_db():
    """
    Drops and re-creates the SQL schema
    """
    db.drop_all()
    db.configure_mappers()
    db.create_all()
    db.session.commit()


if __name__ == '__main__':
    manager.run()

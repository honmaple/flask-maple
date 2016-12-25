#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: runserver.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-12-07 12:59:40 (CST)
# Last Update:星期一 2016-12-12 10:41:2 (CST)
#          By:
# Description:
# **************************************************************************
from flask import Flask, render_template, request, abort
from flask import jsonify
from flask import config
from flask_maple.models import db
from flask_maple.auth.models import User


class Config(object):
    DEBUG = True
    SECRET_KEY = 'asdsad'
    SECURITY_PASSWORD_SALT = ''
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'

    MAIL_SERVER = ''
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = ""
    MAIL_PASSWORD = ""
    MAIL_DEFAULT_SENDER = ''


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    return app


from flask_babelex import Babel, Domain
import os


def register_babel():
    from flask_maple import translations
    translations = translations.__path__[0]
    domain = Domain(translations)
    babel = Babel()

    @babel.localeselector
    def get_locale():
        return 'zh'

    @babel.timezoneselector
    def get_timezone():
        return 'UTC'

    return babel


app = create_app()
db.init_app(app)
register_babel().init_app(app)

from sqlalchemy import inspect
from flask_maple.serializer import Serializer
from flask_maple.utils import get_columns
from flask_maple.views import ViewList, View
from flask_maple.permission.models import Group


class GroupViewList(ViewList):
    model = Group
    serializer_kwargs = {'many': True}


class GroupView(View):
    model = Group
    serializer_kwargs = {'many': False}


app.add_url_rule('/s', view_func=GroupViewList.as_view('s'))
app.add_url_rule('/s/<int:id>', view_func=GroupView.as_view('ss'))

from flask_maple.rbac import rbac


@app.route('/')
def index():
    group = Group.query.filter_by(**{'name': 1}).paginate(1, 1, True)
    a = Serializer(group, many=True, depth=3, exclude=['groups']).data
    from flask_maple.response import HTTPResponse
    from flask_maple.auth.forms import LoginForm
    form = LoginForm()
    print(form.username.label)
    print(form.password.label)
    return HTTPResponse(HTTPResponse.FORBIDDEN).to_response()
    # return jsonify(**a)


if __name__ == '__main__':
    app.run()

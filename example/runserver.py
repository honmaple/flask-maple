#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: runserver.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-12-07 12:59:40 (CST)
# Last Update: Sunday 2018-03-11 14:51:04 (CST)
#          By:
# Description:
# **************************************************************************
from flask import Flask, render_template, request, abort
from flask_wtf.csrf import CsrfProtect
from flask import jsonify
from flask import config
from flask_maple.models import db
from flask_maple.auth.models import User
from flask_maple.auth.views import Auth
from flask_maple.bootstrap import Bootstrap
from flask_maple.captcha import Captcha
from flask_babel import Babel, Domain
from flask_login import LoginManager


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


app = create_app(Config())
Auth(app)
LoginManager(app)
Bootstrap(app, use_auth=True)
CsrfProtect(app)
Captcha(app)

babel = Babel(app)

if __name__ == '__main__':
    app.run()

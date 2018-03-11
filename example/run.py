#!/usr/bin/env python
# -*- coding=UTF-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: run.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-04-16 23:43:21 (CST)
# Last Update: Sunday 2018-03-11 14:51:04 (CST)
#          By:
# Description:
# **************************************************************************
from flask import Flask, render_template, request, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_maple import Captcha, Bootstrap
from flask_maple import Auth, Error
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
from flask_babel import lazy_gettext as _
from flask_login import UserMixin, LoginManager, current_user
from flask_mail import Mail


class Config(object):
    DEBUG = False
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


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
maplec = Captcha(app)
mapleb = Bootstrap(app, use_auth=True)
mail = Mail(app)
babel = Babel(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120), unique=True)

    # def __init__(self):
    # #     self.username = username
    # #     self.email = email
    #     self.password = self.set_password(password)

    def __repr__(self):
        return '<User %r>' % self.name

    @staticmethod
    def set_password(password):
        pw_hash = generate_password_hash(password)
        return pw_hash

    def check_password(self, password):
        return check_password_hash(self.password, password)


Auth(app, db=db, mail=mail, user_model=User)
Error(app)


def register_login(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.session_protection = "strong"
    login_manager.login_message = _("Please login to access this page.")

    return login_manager


from flask_wtf.csrf import CsrfProtect
csrf = CsrfProtect()
csrf.init_app(app)

login_manager = register_login(app)


@babel.localeselector
def get_locale():
    return 'zh'


@babel.timezoneselector
def get_timezone():
    return 'UTC'


@login_manager.user_loader
def user_loader(id):
    user = User.query.get(int(id))
    return user


@app.route('/')
def index():
    data = 'hello world'
    return render_template('index.html', data=data)


if __name__ == '__main__':
    app.run(debug = True)
    print(app.url_map)

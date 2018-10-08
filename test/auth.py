#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: auth.py
# Author: jianglin
# Email: mail@honmaple.com
# Created: 2016-11-01 20:32:54 (CST)
# Last Update: Wednesday 2018-09-26 10:52:52 (CST)
#          By:
# Description:
# **************************************************************************
from main import app, manager, db
from flask_maple.auth.views import Auth
from flask_maple.bootstrap import Bootstrap
from flask_maple.captcha import Captcha
from flask_login import LoginManager
from flask_babel import Babel
from flask_wtf.csrf import CSRFProtect

Auth(app)
Captcha(app)
CSRFProtect(app)

babel = Babel(app)


@babel.localeselector
def get_locale():
    return 'zh'


login_manager = LoginManager(app)
login_manager.login_view = "auth.login"
login_manager.session_protection = "strong"


@login_manager.user_loader
def user_loader(id):
    User = db.Model._decl_class_registry['User']
    user = User.query.get(int(id))
    return user


bootstrap = Bootstrap(app, use_auth=True)

if __name__ == '__main__':
    manager.run()

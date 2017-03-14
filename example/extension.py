#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: extension.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-12-07 13:01:16 (CST)
# Last Update:星期三 2016-12-7 13:1:49 (CST)
#          By:
# Description:
# **************************************************************************
from flask_maple import Captcha, Bootstrap
from flask_maple import Auth, Error
from flask_sqlalchemy import SQLAlchemy
from flask_babelex import Babel
from flask_login import UserMixin, LoginManager, current_user
from flask_mail import Mail

db = SQLAlchemy()
maplec = Captcha()
mapleb = Bootstrap(use_auth=True)
mail = Mail()
babel = Babel()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: extension.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-12-07 13:01:16 (CST)
# Last Update: Sunday 2018-03-11 14:51:04 (CST)
#          By:
# Description:
# **************************************************************************
from flask_maple import Captcha, Bootstrap
from flask_maple import Auth, Error
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
from flask_login import UserMixin, LoginManager, current_user
from flask_mail import Mail

db = SQLAlchemy()
maplec = Captcha()
mapleb = Bootstrap(use_auth=True)
mail = Mail()
babel = Babel()

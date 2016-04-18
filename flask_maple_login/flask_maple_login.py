#!/usr/bin/env python
# -*- coding=UTF-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: flask_maple_login.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-04-16 22:17:32 (CST)
# Last Update: 星期一 2016-4-18 17:57:20 (CST)
#          By:
# Description:
# **************************************************************************
from .views import site


class MapleLogin(object):
    def __init__(self, app=None):
        if app is not None:
            self.app = app
            self.init_app(self.app)
        else:
            self.app = None

    def init_app(self, app):
        self.auth_url = app.config.get('AUTH_URL', '')
        app.register_blueprint(site, url_prefix=self.auth_url)

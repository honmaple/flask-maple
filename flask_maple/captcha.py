#!/usr/bin/env python
# -*- coding=UTF-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: flask_maple_login.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-04-16 22:17:32 (CST)
# Last Update:
#          By:
# Description:
# **************************************************************************
from .validate_code import ValidateCode


class MapleCaptcha(object):
    def __init__(self, app=None):
        if app is not None:
            self.app = app
            self.init_app(self.app)
        else:
            self.app = None

    def init_app(self, app):
        self.captcha = app.config.get('CAPTCHA_URL', 'captcha')
        app.add_url_rule('/' + self.captcha, 'captcha', self.validate)

    def validate(self):
        t = ValidateCode()
        buf = t.start()
        buf_value = buf.getvalue()
        response = self.app.make_response(buf_value)
        response.headers['Content-Type'] = 'image/jpeg'
        return response

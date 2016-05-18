#!/usr/bin/env python
# -*- coding=UTF-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: error.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-05-18 16:34:19 (CST)
# Last Update:星期三 2016-5-18 16:57:10 (CST)
#          By:
# Description:
# **************************************************************************
from flask import render_template


class Error(object):
    def __init__(self, app=None):
        if app is not None:
            self.app = app
            self.init_app(self.app)
        else:
            self.app = None

    def init_app(self, app):
        app.error_handler_spec[None][403] = self.forbidden
        app.error_handler_spec[None][404] = self.not_found
        app.error_handler_spec[None][500] = self.error

    def forbidden(self, error):
        return render_template('templet/error_403.html'), 403

    def not_found(self, error):
        return render_template('templet/error_404.html'), 404

    def error(self, error):
        return render_template('templet/error_500.html'), 500

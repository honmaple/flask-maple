#!/usr/bin/env python
# -*- coding=UTF-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: error.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-05-18 16:34:19 (CST)
# Last Update:星期二 2016-11-8 23:5:32 (CST)
#          By:
# Description:
# **************************************************************************
from flask import render_template, current_app


class Error(object):
    def __init__(self, app=None, use_log=False):
        self.use_log = use_log
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        # try:
        #     app.error_handler_spec[None][403] = self.forbidden
        #     app.error_handler_spec[None][404] = self.not_found
        #     app.error_handler_spec[None][500] = self.error
        # except AttributeError:
        app.register_error_handler(403, self.forbidden)
        app.register_error_handler(404, self.not_found)
        app.register_error_handler(500, self.error)

    def forbidden(self, error):
        current_app.logger.warning(error)
        return render_template('templet/error_403.html'), 403

    def not_found(self, error):
        current_app.logger.info(error)
        return render_template('templet/error_404.html'), 404

    def error(self, error):
        current_app.logger.error(error)
        return render_template('templet/error_500.html'), 500

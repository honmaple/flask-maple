#!/usr/bin/env python
# -*- coding=UTF-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: error.py
# Author: jianglin
# Email: mail@honmaple.com
# Created: 2016-05-18 16:34:19 (CST)
# Last Update: Wednesday 2018-11-21 10:31:57 (CST)
#          By:
# Description:
# **************************************************************************
from flask import render_template, current_app
from flask_maple.response import HTTP


class Error(object):
    def __init__(self, app=None, jsonify=False):
        self.jsonify = jsonify
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.register_error_handler(403, self.forbidden)
        app.register_error_handler(404, self.not_found)
        app.register_error_handler(500, self.error)

    def forbidden(self, error):
        current_app.logger.warning(error)
        if self.jsonify:
            return HTTP.FORBIDDEN()
        return render_template('templet/error_403.html'), 403

    def not_found(self, error):
        current_app.logger.warning(error)
        if self.jsonify:
            return HTTP.NOT_FOUND()
        return render_template('templet/error_404.html'), 404

    def error(self, error):
        current_app.logger.error(error)
        if self.jsonify:
            return HTTP.SERVER_ERROR()
        return render_template('templet/error_500.html'), 500

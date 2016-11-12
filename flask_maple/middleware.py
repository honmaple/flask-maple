#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: middleware.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-11-12 11:56:09 (CST)
# Last Update:星期六 2016-11-12 16:23:50 (CST)
#          By:
# Description:
# **************************************************************************
from flask import request
from werkzeug import import_string
from inspect import isclass


class Middleware(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.middleware = app.config.setdefault('MIDDLEWARE', [])
        app.before_request(self.process_request)

    def process_request(self):
        view_args = request.view_args
        if not view_args:
            view_args = {}
        for middleware_string in self.middleware:
            middleware = import_string(middleware_string)
            if isclass(middleware):
                response = middleware()
                response = response(**view_args)
            else:
                response = middleware(**view_args)
            if response is not None:
                return response

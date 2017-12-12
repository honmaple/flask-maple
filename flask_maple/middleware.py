#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: middleware.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-11-12 11:56:09 (CST)
# Last Update:星期二 2017-12-12 15:22:55 (CST)
#          By:
# Description:
# **************************************************************************
from flask import request
from werkzeug import import_string
import cProfile
import pstats
import sys

if sys.version_info[0] < 3:
    import StringIO
else:
    from io import StringIO


class Middleware(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.middleware = app.config.setdefault('MIDDLEWARE', [])
        self.process(app)

    def process(self, app):
        for middleware_string in self.middleware:
            middleware = import_string(middleware_string)
            response = middleware()
            if hasattr(response, 'preprocess_request'):
                before_request = response.preprocess_request
                app.before_request(before_request)
            if hasattr(response, 'process_response'):
                after_request = response.process_response
                app.after_request(after_request)


class ProfileMiddleware(object):
    def preprocess_request(self):
        pr = cProfile.Profile()
        pr.enable()
        request.pr = pr

    def process_response(self, response):
        pr = request.pr
        pr.disable()
        s = StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return response

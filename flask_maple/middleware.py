#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: middleware.py
# Author: jianglin
# Email: mail@honmaple.com
# Created: 2016-11-12 11:56:09 (CST)
# Last Update: Wednesday 2018-11-21 10:56:12 (CST)
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

try:
    from flask_login import current_user
except ImportError:
    current_user = None


class Middleware(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        middleware = app.config.setdefault('MIDDLEWARE', [])

        for middleware_string in middleware:
            middleware = import_string(middleware_string)
            response = middleware()
            if hasattr(response, 'preprocess_request'):
                before_request = response.preprocess_request
                app.before_request(before_request)
            if hasattr(response, 'process_response'):
                after_request = response.process_response
                app.after_request(after_request)


class RequestMiddleware(object):
    def preprocess_request(self):
        if current_user is not None:
            request.user = current_user._get_current_object()
        if request.method in ["GET", "DELETE"]:
            request.data = request.args.to_dict()
        else:
            request.data = request.json
            if request.data is None:
                request.data = request.form.to_dict()


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

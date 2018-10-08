#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016, 2017 jianglin
# File Name: app.py
# Author: jianglin
# Email: mail@honmaple.com
# Created: 2016-11-12 15:09:30 (CST)
# Last Update: Wednesday 2018-09-26 10:52:51 (CST)
#          By:
# Description:
# **************************************************************************
from flask import send_from_directory, request
from werkzeug import import_string


class App(object):
    def __init__(self, app=None, json=None):
        self.app = app
        self.json = json
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        @app.route('/robots.txt')
        @app.route('/favicon.ico')
        def static_from_root():
            return send_from_directory(app.static_folder, request.path[1:])

        if self.json is not None:
            app.json_encoder = self.json
        self.install_app(app)

    def install_app(self, app):
        install_apps = app.config.setdefault('INSTALLED_APPS', [])
        for blueprint in install_apps:
            kwargs = {}
            if isinstance(blueprint, dict):
                kwargs = blueprint['kwargs']
                blueprint = blueprint['blueprint']
            app.register_blueprint(import_string(blueprint), **kwargs)

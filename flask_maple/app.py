#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: app.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-11-12 15:09:30 (CST)
# Last Update:星期一 2016-11-14 13:39:31 (CST)
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

#!/usr/bin/env python
# -*- coding=UTF-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: bootstrap.py
# Author: jianglin
# Email: mail@honmaple.com
# Created: 2016-04-18 16:03:01 (CST)
# Last Update: Wednesday 2018-11-21 10:22:36 (CST)
#          By: jianglin
# Description: a sample way to use bootstrap
# **************************************************************************
from flask import Blueprint
from flask_assets import Environment, Bundle


class Bootstrap(object):
    def __init__(self, app=None, js=None, css=None, auth=False):
        '''
        auth: if `True`, add login.js to assets
        '''
        self.js = js
        self.css = css
        self.auth = auth
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.blueprint(app)
        self.assets(app)
        self.filters(app)

    def blueprint(self, app):
        blueprint = Blueprint(
            'bootstrap',
            __name__,
            template_folder='templates',
            static_folder='static',
            static_url_path=app.static_url_path + '/bootstrap')

        app.register_blueprint(blueprint)

    def assets(self, app):
        bundles = {
            'home_js':
            Bundle(output='assets/home.js', filters='jsmin'),
            'home_css':
            Bundle(
                'bootstrap/css/honmaple.css',
                output='assets/home.css',
                filters='cssmin')
        }
        if self.auth:
            bundles['home_js'].contents += ('bootstrap/js/login.js', )
        if self.css:
            bundles['home_css'].contents += self.css
        if self.js:
            bundles['home_js'].contents += self.js

        Environment(app).register(bundles)

    def filters(self, app):
        msg = app.config.get('FOOTER_MESSAGE', '')
        app.jinja_env.globals['FOOTER_MESSAGE'] = msg

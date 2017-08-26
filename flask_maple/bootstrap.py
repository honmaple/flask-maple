#!/usr/bin/env python
# -*- coding=UTF-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: flask_maple_bootstrap.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-04-18 16:03:01 (CST)
# Last Update:星期六 2017-8-26 9:12:5 (CST)
#          By: jianglin
# Description: a sample way to use bootstrap
# **************************************************************************
from flask import Blueprint
from flask_assets import Environment, Bundle


class Bootstrap(object):
    def __init__(self, app=None, js=None, css=None, use_auth=False, cdn=True):
        self.js = js
        self.css = css
        self.use_auth = use_auth
        self.cdn = cdn
        self.app = app
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
            'home_js': Bundle(
                output='assets/home.js', filters='jsmin'),
            'home_css': Bundle(
                'bootstrap/css/honmaple.css',
                output='assets/home.css',
                filters='cssmin')
        }
        if not self.cdn:
            bundles['home_js'].contents += (
                'bootstrap/js/jquery.min.js',
                'bootstrap/bootstrap/js/bootstrap.min.js')
            bundles['home_css'].contents += (
                'bootstrap/bootstrap/css/bootstrap.min.css')
        if self.use_auth:
            auth_js = ('bootstrap/js/honmaple.js', 'bootstrap/js/login.js')
            bundles['home_js'].contents += auth_js
        if self.css:
            bundles['home_css'].contents += self.css
        if self.js:
            bundles['home_js'].contents += self.js

        assets = Environment(app)
        assets.register(bundles)

    def filters(self, app):
        author_name = app.config.get('AUTHOR_NAME', 'honmaple')

        def show_footer(author=author_name):
            return author

        app.jinja_env.globals['show_footer'] = show_footer
        app.jinja_env.globals['use_auth'] = self.use_auth
        app.jinja_env.globals['cdn'] = self.cdn

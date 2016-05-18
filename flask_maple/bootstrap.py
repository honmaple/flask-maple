#!/usr/bin/env python
# -*- coding=UTF-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: flask_maple_bootstrap.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-04-18 16:03:01 (CST)
# Last Update:星期三 2016-5-18 20:48:6 (CST)
#          By: jianglin
# Description:
# **************************************************************************
from flask import Blueprint
from flask_assets import Environment, Bundle


class MapleBootstrap(object):
    def __init__(self, app=None, js=None, css=None):
        self.js = js
        self.css = css
        if app is not None:
            self.app = app
            self.init_app(self.app)
        else:
            self.app = None

    def init_app(self, app):
        self.author_name = app.config.get('AUTHOR_NAME', 'honmaple')
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
            'home_js': Bundle('bootstrap/js/jquery.min.js',
                              'bootstrap/js/bootstrap.min.js',
                              'bootstrap/js/honmaple.js',
                              'bootstrap/js/login.js',
                              output='assets/home.js',
                              filters='jsmin'),
            'home_css': Bundle('bootstrap/css/bootstrap.min.css',
                               'bootstrap/css/honmaple.css',
                               output='assets/home.css',
                               filters='cssmin')
        }
        if self.css:
            bundles['home_css'].contents = bundles[
                'home_css'].contents + self.css
        if self.js:
            bundles['home_css'].contents = bundles[
                'home_js'].contents + self.js

        assets = Environment(app)
        assets.register(bundles)

    def filters(self, app):
        def show_footer(author=self.author_name):
            return author

        app.jinja_env.globals['show_footer'] = show_footer

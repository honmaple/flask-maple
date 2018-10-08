#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: lazy.py
# Author: jianglin
# Email: mail@honmaple.com
# Created: 2016-11-08 23:02:24 (CST)
# Last Update: Wednesday 2018-09-26 10:52:51 (CST)
#          By:
# Description:
# **************************************************************************
from werkzeug import import_string, cached_property


class LazyView(object):
    def __init__(self, app=None, url=None, name=None, **options):
        self.app = app
        self.url = url
        self.name = name
        self.options = options
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.add_url_rule(self.url, view_func=self.view, **self.options)

    @cached_property
    def view(self):
        view = import_string(self.name)
        if isinstance(view, (object, )):
            assert self.options.get('endpoint') is not None
            endpoint = self.options.pop('endpoint')
            view = view.as_view(endpoint)
        return view


class LazyBlueprint(object):
    def __init__(self, app=None, blueprint=None, module='app.', **options):
        self.app = app
        self.module = module
        self.blueprint = blueprint
        self.options = options
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if isinstance(self.blueprint, (list, tuple)):
            self._multi(app)
        else:
            self._single(app)

    def _single(self, app):
        blueprint = import_string(self.module + self.blueprint)
        app.register_blueprint(blueprint, **self.options)

    def _multi(self, app):
        blueprints = list(set(self.blueprint))
        for name in blueprints:
            blueprint = import_string(self.module + name)
            app.register_blueprint(blueprint, **self.options)


class LazyExtension(object):
    def __init__(self, app=None, extension=None, module='app.extensions.'):
        self.app = app
        self.module = module
        self.extension = extension
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if isinstance(self.extension, (list, tuple)):
            self._multi(app)
        else:
            self._single(app)

    def _single(self, app):
        extension = import_string(self.module + self.extension)
        extension.init_app(app)

    def _multi(self, app):
        extensions = list(set(self.extension))
        for name in extensions:
            extension = import_string(self.module + name)
            extension.init_app(app)

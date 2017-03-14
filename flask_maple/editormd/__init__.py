#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: __init__.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-12-02 15:52:51 (CST)
# Last Update:星期二 2017-3-14 21:24:29 (CST)
#          By:
# Description:
# **************************************************************************
from .fields import _editormd


class EditorMd(object):
    def __init__(self, app=None, static_file=None, config=None, cdn=False):
        self.app = app
        self.cdn = cdn
        self.config = config
        self.static_file = static_file
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.filters(app)

    def filters(self, app):
        app.jinja_env.globals['editormd'] = _editormd(
            cdn=self.cdn, static_file=self.static_file, config=self.config)

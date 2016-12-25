#!/usr/bin/env python
# -*- coding=UTF-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: rbac.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-07-22 19:40:16 (CST)
# Last Update:星期六 2016-12-10 15:36:38 (CST)
#          By:
# Description:
# **************************************************************************
from flask import abort
from functools import wraps


class Rbac(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        pass

    def require(self, groups, callback=lambda: abort(404)):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kw):
                print(groups)
                return func(*args, **kw)

            return wrapper

        return decorator


rbac = Rbac()

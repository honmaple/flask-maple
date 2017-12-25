#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: __init__.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-12-05 11:24:11 (CST)
# Last Update:星期一 2017-12-25 16:56:23 (CST)
#          By:
# Description:
# **************************************************************************
from flask import request, abort
from functools import wraps


class MethodViewPermission(object):
    decorators = ()

    def __call__(self, func):
        f = self.method(func)
        if self.decorators:
            for dec in reversed(self.decorators):
                f = dec(f)
        return f

    def method(self, func):
        @wraps(func)
        def decorator(*args, **kwargs):
            meth = getattr(self, request.method.lower(), None)
            if request.method == 'HEAD':
                meth = getattr(self, 'get', None)
            if meth is not None:
                check = meth(*args, **kwargs)
                if isinstance(check, bool) and check:
                    return func(*args, **kwargs)
                elif callable(check):
                    return check()
                elif check:
                    return check or self.callback()
            return func(*args, **kwargs)

        return decorator

    def callback(self):
        abort(403)

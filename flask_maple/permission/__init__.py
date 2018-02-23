#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: __init__.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-12-05 11:24:11 (CST)
# Last Update: 星期五 2018-02-23 10:49:12 (CST)
#          By:
# Description:
# **************************************************************************
from flask import request, abort, g
from functools import wraps


def is_allowed(groups=[], resource_type='endpoint', response=None):
    def _is_allowed(func):
        @wraps(func)
        def _wraps(*args, **kwargs):
            user = g.user
            user_in_groups = user.groups.filter_by(name__in=groups).exists()
            if user_in_groups or user.has_perm(request.method,
                                               request.blueprint):
                return func(*args, **kwargs)
            if response is None:
                abort(403)
            elif callable(response):
                return response()
            else:
                return response

        return _wraps

    return _is_allowed


def is_denied(groups=[], resource_type='endpoint', response=None):
    def _is_denied(func):
        @wraps(func)
        def _wraps(*args, **kwargs):
            user = g.user
            user_in_groups = user.groups.filter_by(name__in=groups).exists()
            if user_in_groups or user.has_perm(request.method,
                                               request.blueprint):
                return func(*args, **kwargs)
            if response is None:
                abort(403)
            elif callable(response):
                return response()
            else:
                return response
        return _wraps

    return _is_denied


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

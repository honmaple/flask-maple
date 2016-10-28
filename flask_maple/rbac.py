#!/usr/bin/env python
# -*- coding=UTF-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: rbac.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-07-22 19:40:16 (CST)
# Last Update:星期日 2016-7-31 22:33:48 (CST)
#          By:
# Description:
# **************************************************************************
from flask import request, abort


class Rbac(object):
    def __init__(self,
                 app=None,
                 skip_startswith_rules=['/admin', '/static'],
                 skip_rules=['static'],
                 **kwargs):
        self.skip_startswith_rules = skip_startswith_rules
        self.skip_rules = skip_rules
        self._role_model = kwargs.get('role_model')
        self._route_model = kwargs.get('route_model')
        self._permission_model = kwargs.get('permission_model')
        self._user_loader = kwargs.get('user_loader')
        self.callback = kwargs.get('callback', lambda: abort(403))
        if app is not None:
            self.app = app
            self.init_app(app)
        else:
            self.app = None

    def init_app(self, app):
        app.before_request(self._before_request)

    def check_deny(self):
        deny_rules = self._permission_model.query.join(
            self._permission_model.routes).filter(
                self._route_model.endpoint == request.endpoint,
                self._route_model.rule == request.url,
                self._permission_model.is_allow == False).all()
        for permission in deny_rules:
            roles = set(self._user_loader.roles).intersection(set(
                permission.roles))
            if roles:
                return False
        return True

    def check_allow(self):
        allow_rules = self._permission_model.query.join(
            self._permission_model.routes).filter(
                self._route_model.endpoint == request.endpoint,
                self._route_model.rule == request.url,
                self._permission_model.is_allow == True).all()
        for permission in allow_rules:
            roles = set(self._user_loader.roles).intersection(set(
                permission.roles))
            if not roles:
                return False
        return True

    def check_anonymous(self):
        deny_rules = self._permission_model.query.join(
            self._permission_model.routes,
            self._permission_model.roles).filter(
                self._route_model.endpoint == request.endpoint,
                self._route_model.rule == request.url,
                self._role_model.name == 'anonymous',
                self._permission_model.is_allow == False).all()
        if deny_rules:
            return False
        return True

    def _before_request(self):
        assert self._route_model, "Please set route model."
        assert self._permission_model, "Please set permission model."
        assert self._user_loader, "Please set user loader."
        go_one = True
        go_two = True
        for i in self.skip_startswith_rules:
            if request.path.startswith(i):
                go_one = False
                break
        for i in self.skip_rules:
            if request.endpoint == i:
                go_two = False
                break
        if go_one and go_two:
            if self._user_loader.is_authenticated:
                if not self.check_deny():
                    return self.callback()
                if not self.check_allow():
                    return self.callback()
            else:
                if not self.check_anonymous():
                    return self.callback()

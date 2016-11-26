#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: middleware.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-11-25 17:34:29 (CST)
# Last Update:星期六 2016-11-26 16:48:53 (CST)
#          By:
# Description:
# **************************************************************************
from flask import g, request, abort, current_app
from flask_maple.response import HTTPResponse
from sqlalchemy import or_
from .models import Group, Router, Permission
import re


class PermissionMiddleware(object):
    @property
    def skip_endpoint(self):
        return ['static', 'static_from_root', 'bootstrap.static']

    @property
    def skip_url(self):
        return []

    @property
    def skip_regex_url(self):
        return ['^/admin']

    def _get_router(self):
        router = Router.query.filter_by(
            url=request.path, url_type=Router.URL_TYPE_HTTP).first()
        if router is None:
            router = Router.query.filter_by(
                url=request.endpoint,
                url_type=Router.URL_TYPE_ENDPOINT).first()
        return router

    def _has_perm(self, group_perm_list, perm_list):
        if not perm_list:
            return False
        common_perm_list = set(group_perm_list) & set(perm_list)
        if common_perm_list:
            return True
        return False

    def _has_allow_perm(self, group_perm_list):
        method_name = 'ALLOW_ALL_' + request.method.upper()
        perm_list = Permission.query.filter(
            or_(Permission.name == 'ALLOW_ALL', Permission.name ==
                method_name)).all()
        return self._has_perm(group_perm_list, perm_list)

    def _has_deny_perm(self, group_perm_list):
        method_name = 'DENY_ALL_' + request.method.upper()
        perm_list = Permission.query.filter(
            or_(Permission.name == 'DENY_ALL', Permission.name ==
                method_name)).all()
        return self._has_perm(group_perm_list, perm_list)

    def _get_permissions(self, groups):
        permissions = []
        for group in groups:
            perm_list = group.permissions.all()
            for p in perm_list:
                permissions.append(p)
        return permissions

    def has_perm(self):
        user = g.user

        if user.is_active and user.is_superuser:
            return True
        if user.is_authenticated:
            groups = Group.query.filter(
                or_(Group.name == 'authenticated', Group.users.contains(
                    user))).all()
            if not groups:
                group = Group()
                group.name = 'authenticated'
                group.save()
                groups = [group]
        else:
            groups = Group.query.filter_by(name='anonymous').all()
            if not groups:
                group = Group()
                group.name = 'anonymous'
                group.save()
                groups = [group]
        group_perm_list = self._get_permissions(groups)
        current_app.logger.debug(
            'current groups are: %s' % groups)
        current_app.logger.debug(
            'current groups permissions are: %s' % group_perm_list)
        if self._has_deny_perm(group_perm_list):
            return False
        router = self._get_router()
        if router is not None:
            deny_perm_list = router.get_deny_method_permissions(request.method)
            if self._has_perm(group_perm_list, deny_perm_list):
                return False
        if self._has_allow_perm(group_perm_list):
            return True
        if router is not None:
            allow_perm_list = router.get_allow_method_permissions(
                request.method)
            if self._has_perm(group_perm_list, allow_perm_list):
                return True
        return False

    def preprocess_request(self):
        url = request.path
        endpoint = request.endpoint
        current_app.logger.debug(
            'current url is: %s\ncurrent endpoint is: %s' % (url, endpoint))
        if url in self.skip_url:
            return
        if endpoint in self.skip_endpoint:
            return
        for regex_url in self.skip_regex_url:
            pattern = re.compile(regex_url)
            if bool(pattern.match(request.path)):
                return
        if not self.has_perm():
            return self.callback()

    def callback(self):
        abort(403)
        # return HTTPResponse(HTTPResponse.FORBIDDEN).to_response()

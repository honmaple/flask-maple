#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: middleware.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-11-25 17:34:29 (CST)
# Last Update:星期五 2016-11-25 17:49:30 (CST)
#          By:
# Description:
# **************************************************************************
from flask import g, request
from flask_maple.response import HTTPResponse
from sqlalchemy import or_
from .models import Group, Router, Permission


class PermissionMiddleware(object):
    def _get_router(self, request):
        try:
            url = resolve(request.path)
            router = Router.objects.get(url=url.view_name,
                                            url_type=Router.URL_TYPE_FUNC)
            return router
        except Router.DoesNotExist:
            return

    def _has_perm(self, group_perm_list, perm_list):
        if not perm_list:
            return False
        common_perm_list = set(group_perm_list) & set(perm_list)
        if common_perm_list:
            return True
        return False

    def _has_allow_perm(self, request, group_perm_list):
        method_name = 'allow_all_' + request.method.lower()
        perm_list = Permission.objects.filter(
            Q(name='allow_all') | Q(name=method_name))
        return self._has_perm(group_perm_list, perm_list)

    def _has_deny_perm(self, request, group_perm_list):
        method_name = 'deny_all_' + request.method.lower()
        perm_list = Permission.objects.filter(
            Q(name='deny_all') | Q(name=method_name))
        return self._has_perm(group_perm_list, perm_list)

    def get_all_permission(self, groups):
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
        if user.is_authenticated():
            groups = Group.query.filter_by(
                or_(name='LOGINED', users__id=user.id))
            if not groups:
                group = Group()
                group = 'LOGINED'
                group.save()
                groups = [group]
        else:
            groups = Group.query.filter_by(name='anonymous')
            if not groups:
                group = Group()
                group = 'anonymous'
                group.save()
                groups = [group]
        group_perm_list = self.get_all_permission(groups)
        if self._has_deny_perm(group_perm_list):
            return False
        router = self.get_router()
        if router is not None:
            deny_perm_list = router.get_deny_method_permissions(request.method)
            if self._has_perm(group_perm_list, deny_perm_list):
                return False
        if self._has_allow_perm(request, group_perm_list):
            return True
        if router is not None:
            allow_perm_list = router.get_allow_method_permissions(
                request.method)
            if self._has_perm(group_perm_list, allow_perm_list):
                return True
        return False

    def preprocess_request(self):
        if not self.has_perm():
            return HTTPResponse(HTTPResponse.FORBIDDEN).to_response()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: models.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-11-25 16:44:19 (CST)
# Last Update:星期五 2016-11-25 17:34:4 (CST)
#          By:
# Description:
# **************************************************************************
from flask_maple.models import db

group_permission = db.Table(
    'group_permission',
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id')),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id')))

router_permission = db.Table(
    'router_permission',
    db.Column('router_id', db.Integer, db.ForeignKey('routers.id')),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id')))


class Permission(db.Model):
    __tablename__ = 'permissions'

    METHOD_GET = '0'
    METHOD_POST = '1'
    METHOD_PUT = '2'
    METHOD_DELETE = '3'
    METHOD_PATCH = '4'
    METHOD_ALL = '5'

    METHOD = (('0', 'GET 方式'), ('1', 'POST 方式'), ('2', 'PUT 方式'),
              ('3', 'DELETE 方式'), ('4', 'PATCH 方式'), ('5', '所有方式'))

    PERMISSION_DENY = '0'
    PERMISSION_ALLOW = '1'

    PERMISSION = (('0', '禁止'), ('1', '允许'))

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(512), nullable=False)
    allow = db.Column(db.String(10), default=PERMISSION_ALLOW)
    method = db.Column(db.String(16), default=METHOD_GET)

    def __repr__(self):
        return "<Permission %r>" % self.name

    def is_allowed(self):
        if self.allow == self.PERMISSION_ALLOW:
            return True
        return False

    def is_denied(self):
        if self.allow == self.PERMISSION_DENY:
            return True
        return False


class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(512), nullable=False)
    permissions = db.relationship(
        Permission, secondary=group_permission, backref=db.backref('groups'))

    def __repr__(self):
        return "<Group %r>" % self.name

    def get_permissions(self):
        return self.permissions.all()

    def has_perm(self, perm):
        if perm in self.get_permissions():
            return True
        return False

    def has_perms(self, perm_list):
        router_perm_list = set(perm_list)
        group_perm_list = set(self.get_permissions())
        common_perm_list = router_perm_list & group_perm_list
        if not common_perm_list:
            return False
        return True


class Router(db.Model):
    __tablename__ = 'routers'

    URL_TYPE_HTTP = '0'
    URL_TYPE_FUNC = '1'
    URL_TYPE = (('0', 'http形式'), ('1', '函数形式'))

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(512), nullable=False)
    url_type = db.Column(db.String(10), default=URL_TYPE_HTTP)
    description = db.Column(db.String(128), nullable=False)
    rule = db.Column(db.String(512), nullable=False)
    permissions = db.relationship(
        Permission, secondary=router_permission, backref=db.backref('routers'))

    def __repr__(self):
        return "<Router %r>" % self.url

    def _get_filter_dict(self, method):
        filter_dict = {}
        if method == "HEAD":
            method = "GET"
        if hasattr(Permission, 'METHOD_' + method):
            filter_dict.update(method=getattr(Permission,
                                              'METHOD_' + method))
        return filter_dict

    def get_permissions(self):
        return self.permissions.all()

    def get_allow_permissions(self):
        return self.permissions.filter(allow=Permission.PERMISSION_ALLOW)

    def get_deny_permissions(self):
        return self.permissions.filter(allow=Permission.PERMISSION_DENY)

    def get_method_permissions(self, method):
        filter_dict = self._get_filter_dict(method)
        return self.permissions.filter(**filter_dict)

    def get_allow_method_permissions(self, method):
        filter_dict = self._get_filter_dict(method)
        filter_dict.update(allow=Permission.PERMISSION_ALLOW)
        return self.permissions.filter(**filter_dict)

    def get_deny_method_permissions(self, method):
        filter_dict = self._get_filter_dict(method)
        filter_dict.update(allow=Permission.PERMISSION_DENY)
        return self.permissions.filter(**filter_dict)
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: models.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-08-29 16:47:32 (CST)
# Last Update:星期二 2017-12-05 11:33:52 (CST)
#          By:
# Description:
# **************************************************************************
from sqlalchemy.ext.declarative import declared_attr
from functools import wraps
from flask_maple.models import ModelMixin, db

user_permission = db.Table(
    'user_permission',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id')))

group_permission = db.Table(
    'group_permission',
    db.Column('group_id', db.Integer, db.ForeignKey('group.id')),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id')))


class UserMixin(object):
    def perm_cache(func):
        @wraps(func)
        def _perm_cache(self, *args, **kwargs):

            return func(self, *args, **kwargs)

        return _perm_cache

    @perm_cache
    def has_perm(self, perm_code):
        perm_codes = perm_code if isinstance(perm_code,
                                             (list, tuple)) else [perm_code]
        if self.filter_by(permissions__code__in=perm_codes).exists():
            return True
        if self.filter_by(groups__permissions__code__in=perm_codes).exists():
            return True
        if self.filter_by(
                groups__child_groups__permissions__code__in=perm_codes).exists(
                ):
            return True
        return False

    def has_operate_perm(self, operate, model):
        _operate = self._operate
        operate = operate.upper()
        if operate not in _operate:
            return False
        operate = _operate[operate]
        model = model.__tablename__ if not isinstance(model, str) else model
        # 01 允许操作  00 不允许操作
        deny_perm_code = '{}:00{}'.format(model, operate)
        allow_perm_code = '{}:01{}'.format(model, operate)
        if self.has_perm(deny_perm_code):
            return False
        if self.has_perm(allow_perm_code):
            return True
        return False

    def has_access_perm(self, access, api):
        apis = api if isinstance(api, (list, tuple)) else [api]
        _access = self._access
        access = access.upper()
        if access not in _access:
            return False
        access = _access[access]
        deny_perm_codes = ['{}:10{}'.format(api, access) for api in apis]
        allow_perm_codes = ['{}:11{}'.format(api, access) for api in apis]
        if self.has_perm(deny_perm_codes):
            return False
        if self.has_perm(allow_perm_codes):
            return True
        return False

    @property
    def _access(self):
        '''
        接口访问权限
        :code 00:api
        user access api allow

        100 不允许GET方式    110 允许GET方式
        101 不允许POST方式   111 允许POST方式
        102 不允许PUT方式    112 允许PUT方式
        103 不允许DELETE方式 113 允许DELETE方式
        '''
        return self.permissions.ACCESS

    @property
    def _operate(self):
        '''
        数据库操作权限
        :code 00:model
        :example OPERATE:MODEL:ALLOW:INSERT model:011
        use operate model allow

        000 不允许SELECT    010 允许SELECT
        001 不允许INSERT    011 允许INSERT
        002 不允许UPDATE    012 允许UPDATE
        003 不允许DELETE    013 允许DELETE
        '''
        return self.permissions.OPERATE


class GroupMixin(UserMixin):
    def perm_cache(func):
        return UserMixin.perm_cache

    @perm_cache
    def has_perm(self, perm_code):
        perm_codes = perm_code if isinstance(perm_code,
                                             (list, tuple)) else [perm_code]
        if self.filter_by(permissions__code__in=perm_codes).exists():
            return True
        if self.filter_by(
                child_groups__permissions__code__in=perm_codes).exists():
            return True
        return False


class PermissionMixin(ModelMixin):
    OPERATE = {'SELECT': '0', 'INSERT': '1', 'UPDATE': '2', 'DELETE': '3'}
    ACCESS = {'GET': '0', 'POST': '1', 'PUT': '2', 'DELETE': '3'}

    @declared_attr
    def name(cls):
        return db.Column(db.String(81), nullable=False)

    @declared_attr
    def code(cls):
        return db.Column(db.String(81), nullable=False)

    @declared_attr
    def description(cls):
        return db.Column(db.Text(2048), nullable=False)

    @declared_attr
    def users(cls):
        return db.relationship(
            'User',
            secondary=user_permission,
            backref=db.backref(
                'permissions', lazy='dynamic'),
            lazy='dynamic')

    @declared_attr
    def groups(cls):
        return db.relationship(
            'Group',
            secondary=group_permission,
            backref=db.backref(
                'permissions', lazy='dynamic'),
            lazy='dynamic')

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: models.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-08-29 16:47:32 (CST)
# Last Update: 星期五 2018-02-23 22:59:49 (CST)
#          By:
# Description:
# **************************************************************************
from sqlalchemy.ext.declarative import declared_attr
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
    def perm_cache(self,
                   action,
                   resource,
                   resource_type='endpoint',
                   and_=False):
        return

    def add_perm(self,
                 action,
                 resource,
                 resource_type='endpoint',
                 description=None):
        '''
        if `resource_type == 'model', action is in `[intert, delete, update, select]``
        else action is in `[post, delete, put, get]`
        '''
        action = self._perm_action(action, resource_type)
        perm = self.permissions.filter_by(
            resource=resource, resource_type=resource_type).one_or_none()
        if not perm:
            perm_model = self.__class__.permissions.property.mapper.class_
            perm = perm_model(resource=resource, resource_type=resource_type)
            perm.code = '0000'
        code = list(perm.code)
        code[action] = '1'
        perm.code = ''.join(code)
        if description is not None:
            perm.description = description
        perm.save()
        self.permissions.append(perm)
        return perm

    def remove_perm(self, action, resource, resource_type='endpoint'):
        action = self._perm_action(action, resource_type)
        perm = self.permissions.filter_by(
            resource=resource, resource_type=resource_type).one_or_none()
        if not perm:
            return
        code = list(perm.code)
        code[action] = '0'
        perm.code = ''.join(code)
        perm.save()
        return perm

    def _perms(self, resource, resource_type):
        perm_model = self.__class__.permissions.property.mapper.class_
        groups = self.groups.all()
        groups.extend([
            g for group in groups for g in group.get_child_groups(3)
        ])
        groups = list(set(groups))
        group_perms = perm_model.query.filter_by(
            resource=resource,
            resource_type=resource_type,
            groups__id__in=[g.id for g in groups]).all()
        user_perms = self.permissions.filter_by(
            resource=resource, resource_type=resource_type).all()
        return list(set(user_perms) | set(group_perms))

    def _perm_action(self, action, resource_type):
        action = action.lower()
        operate = {'insert': 0, 'delete': 1, 'update': 2, 'select': 3}
        access = {'post': 0, 'delete': 1, 'put': 2, 'get': 3}
        if resource_type == 'model':
            action = operate.get(action)
        else:
            action = access.get(action)
        return action

    def has_perm(self, action, resource, resource_type='endpoint', and_=False):
        perm_cache = self.perm_cache(action, resource, resource_type, and_)
        if perm_cache is not None:
            return perm_cache
        if isinstance(resource, (list, tuple)):
            is_allowed = False
            for r in resource:
                _is_allowed = self.has_perm(action, r, resource_type, and_)
                # and: 全部允许才允许
                if and_ and not _is_allowed:
                    return False
                # or: 有一个允许就允许
                if not and_ and _is_allowed:
                    return True

                is_allowed = is_allowed | _is_allowed
            return is_allowed

        action = self._perm_action(action, resource_type)
        if action is None:
            return False

        perm = 0b0
        for p in self._perms(resource, resource_type):
            perm = perm | int(p.code[action], 2)
        return perm > 0

    def has_operate_perm(self,
                         action,
                         resource,
                         resource_type='model',
                         and_=False):
        return self.has_perm(action, resource, resource_type, and_)

    def has_access_perm(self,
                        action,
                        resource,
                        resource_type='endpoint',
                        and_=False):
        return self.has_perm(action, resource, resource_type, and_)

    def is_creatable(self, code):
        return 2**3 >= code

    def is_deletable(self, code):
        return 2**2 >= code

    def is_writable(self, code):
        return 2**1 >= code

    def is_readable(self, code):
        return 2**0 >= code


class GroupMixin(UserMixin):
    def _perms(self, resource, resource_type):
        perm_model = self.__class__.permissions.property.mapper.class_
        groups = self.get_child_groups(3)
        groups.append(self)
        groups = list(set(groups))
        group_perms = perm_model.query.filter_by(
            resource=resource,
            resource_type=resource_type,
            groups__id__in=[group.id for group in groups]).all()
        return group_perms


class PermissionMixin(ModelMixin):
    @declared_attr
    def code(cls):
        return db.Column(db.String(81), default='0000')

    @declared_attr
    def resource(cls):
        return db.Column(db.String(1024), nullable=False)

    @declared_attr
    def resource_type(cls):
        return db.Column(db.String(81), nullable=False)

    @declared_attr
    def description(cls):
        return db.Column(db.String(2048))

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

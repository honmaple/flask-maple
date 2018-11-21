#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ********************************************************************************
# Copyright © 2018 jianglin
# File Name: permission.py
# Author: jianglin
# Email: mail@honmaple.com
# Created: 2018-09-04 18:26:49 (CST)
# Last Update: Wednesday 2018-11-21 11:13:25 (CST)
#          By:
# Description:
# ********************************************************************************
from sqlalchemy.ext.declarative import declared_attr
from flask_maple.models import ModelMixin, db


class UserMixin(object):
    def _has_perm(self, code, need_code, and_):
        p = code & need_code > 0
        if and_:
            return code >= need_code and p
        return p

    def _get_action_map(self, action):
        action = action.upper()
        return {
            "POST": 8,
            "DELETE": 4,
            "PUT": 2,
            "GET": 1,
            "INSERT": 8,
            "UPDATE": 2,
            "SELECT": 1,
        }.get(action, 0)

    def get_perm_or_create(self, resource, resource_type='endpoint'):
        p = self.permissions.filter_by(
            resource=resource,
            resource_type=resource_type,
        ).first()
        if not p:
            perm_model = self.__class__.permissions.property.mapper.class_
            p = perm_model(
                resource=resource,
                resource_type=resource_type,
                identity_id=self.id,
                code=0)
            p.save()
        return p

    def add_perm(self,
                 actions,
                 resource,
                 resource_type='endpoint',
                 reset=False):
        if isinstance(actions, str):
            actions = [actions]
        p = self.get_perm_or_create(
            resource=resource,
            resource_type=resource_type,
        )
        need_code = sum([self._get_action_map(action) for action in actions])
        p.code = p.code | need_code
        p.save()
        return p

    def remove_perm(self,
                    actions,
                    resource,
                    resource_type='endpoint',
                    reset=False):
        '''
        remove perm mean add deny permission
        '''
        if isinstance(actions, str):
            actions = [actions]
        p = self.get_perm_or_create(
            resource=resource,
            resource_type=resource_type,
        )

        need_code = sum([self._get_action_map(action) for action in actions])
        p.code = (p.code ^ need_code) & p.code
        if reset and p.code == 0:
            p.delete()
        else:
            p.save()
        return p

    def has_perm(self,
                 actions,
                 resource,
                 resource_type='endpoint',
                 and_=True,
                 res_and_=True,
                 ignore_group=False,
                 default=False,
                 depth=3):
        if isinstance(resource, (list, tuple)):
            return self.has_perms(actions, resource, resource_type, and_,
                                  res_and_)
        if isinstance(actions, str):
            actions = [actions]

        need_code = sum([self._get_action_map(action) for action in actions])

        p = self.permissions.filter_by(
            resource=resource,
            resource_type=resource_type,
        ).first()

        code = p.code if p else 15 if default else 0

        if p and not self._has_perm(code, need_code, and_):
            return False

        if ignore_group:
            return self._has_perm(code, need_code, and_)

        groups = self.groups.all()
        if not groups:
            return self._has_perm(code, need_code, and_)

        for group in groups:
            _has_perm = group.has_perm(
                actions=actions,
                resource=resource,
                resource_type=resource_type,
                and_=and_,
                res_and_=res_and_,
                ignore_group=ignore_group,
                default=default,
                depth=depth)
            if not _has_perm:
                return False
        return True

    def has_perms(self,
                  actions,
                  resources,
                  resource_type='endpoint',
                  and_=True,
                  res_and_=True,
                  ignore_group=False,
                  default=False,
                  depth=3):
        if isinstance(resources, str):
            resources = [resources]

        _has_perm = False
        for resource in resources:
            _has_perm = self.has_perm(
                actions=actions,
                resource=resource,
                resource_type=resource_type,
                and_=and_,
                ignore_group=ignore_group,
                default=default,
                depth=depth)
            if res_and_ and not _has_perm:
                return False
            if not res_and_ and _has_perm:
                return True
        return _has_perm


class GroupMixin(UserMixin):
    def has_perm(self,
                 actions,
                 resource,
                 resource_type='endpoint',
                 and_=True,
                 res_and_=True,
                 ignore_group=False,
                 default=False,
                 depth=3):
        if isinstance(resource, (list, tuple)):
            return self.has_perms(actions, resource, resource_type, and_,
                                  res_and_)
        if isinstance(actions, str):
            actions = [actions]

        need_code = sum([self._get_action_map(action) for action in actions])

        p = self.permissions.filter_by(
            resource=resource,
            resource_type=resource_type,
        ).first()

        code = p.code if p else 15 if default else 0

        if p and not self._has_perm(code, need_code, and_):
            return False

        if ignore_group:
            return self._has_perm(code, need_code, and_)

        parent_group = self.parent_group
        if not parent_group:
            return self._has_perm(code, need_code, and_)

        return parent_group.has_perm(
            actions=actions,
            resource=resource,
            resource_type=resource_type,
            and_=and_,
            res_and_=res_and_,
            ignore_group=ignore_group,
            default=default,
            depth=depth - 1)


class PermissionMixin(ModelMixin):
    @declared_attr
    def code(cls):
        return db.Column(db.Integer, default=0)

    @declared_attr
    def resource(cls):
        return db.Column(db.String(1024), nullable=False)

    @declared_attr
    def resource_type(cls):
        return db.Column(db.String(81), nullable=False)

    @declared_attr
    def description(cls):
        return db.Column(db.String(2048))

    @classmethod
    def resources(cls, resource_type="endpoint"):
        return [
            i.resource for i in cls.query.filter_by(
                resource_type=resource_type).group_by(cls.resource)
        ]


class UserPermissionMixin(PermissionMixin):
    @declared_attr
    def identity_id(cls):
        return db.Column(
            db.Integer,
            db.ForeignKey('user.id', ondelete="CASCADE"),
            nullable=False)

    @declared_attr
    def identity(cls):
        return db.relationship(
            'User',
            backref=db.backref(
                'permissions', cascade='all,delete-orphan', lazy='dynamic'),
            uselist=False,
            lazy='joined')


class GroupPermissionMixin(PermissionMixin):
    @declared_attr
    def identity_id(cls):
        return db.Column(
            db.Integer,
            db.ForeignKey('group.id', ondelete="CASCADE"),
            nullable=False)

    @declared_attr
    def identity(cls):
        return db.relationship(
            'Group',
            backref=db.backref(
                'permissions', cascade='all,delete-orphan', lazy='dynamic'),
            uselist=False,
            lazy='joined')

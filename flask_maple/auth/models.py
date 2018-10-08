#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: models.py
# Author: jianglin
# Email: mail@honmaple.com
# Created: 2016-12-07 13:12:42 (CST)
# Last Update: Wednesday 2018-09-26 10:52:50 (CST)
#          By:
# Description:
# **************************************************************************
from datetime import datetime
from sqlalchemy.ext.declarative import declared_attr

from flask_login import UserMixin as _UserMixin
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from flask_maple.models import ModelMixin, db
from flask_maple.mail import MailMixin

user_group = db.Table(
    'user_group', db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id')))


class GroupMixin(ModelMixin):
    @declared_attr
    def id(cls):
        return db.Column(db.Integer, primary_key=True)

    @declared_attr
    def name(cls):
        return db.Column(db.String(512), nullable=False, unique=True)

    @declared_attr
    def parent_id(cls):
        return db.Column(db.Integer, db.ForeignKey('group.id'))

    @declared_attr
    def parent_group(cls):
        return db.relationship(
            'Group',
            remote_side=[cls.id],
            backref=db.backref(
                'child_groups', remote_side=[cls.parent_id], lazy='dynamic'),
            lazy='joined',
            uselist=False)

    def get_child_groups(self, depth=1):
        child_groups = self.child_groups.all()
        depth -= 1
        if depth > 0:
            child_groups.extend([
                g for group in child_groups
                for g in group.get_child_groups(depth)
            ])
        return list(set(child_groups))

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Group %r>' % self.name


class UserMixin(_UserMixin, MailMixin, ModelMixin):
    @declared_attr
    def id(cls):
        return db.Column(db.Integer, primary_key=True)

    @declared_attr
    def username(cls):
        return db.Column(db.String(512), nullable=False, unique=True)

    @declared_attr
    def email(cls):
        return db.Column(db.String(512), nullable=False, unique=True)

    @declared_attr
    def password(cls):
        return db.Column(db.String(512), nullable=False)

    @declared_attr
    def is_superuser(cls):
        return db.Column(db.Boolean, default=False)

    @declared_attr
    def is_confirmed(cls):
        return db.Column(db.Boolean, default=False)

    @declared_attr
    def register_time(cls):
        return db.Column(db.DateTime, default=datetime.now)

    @declared_attr
    def last_login(cls):
        return db.Column(db.DateTime, default=datetime.now)

    @declared_attr
    def groups(cls):
        return db.relationship(
            'Group',
            secondary=user_group,
            backref=db.backref('users', lazy='dynamic'),
            lazy='dynamic')

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)
        return self.password

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    @property
    def is_logined(self):
        return self.is_authenticated

    def login(self, remember=True):
        login_user(self, remember)

    def logout(self):
        logout_user()

    def __str__(self):
        return self.username

    def __repr__(self):
        return '<User %r>' % self.username

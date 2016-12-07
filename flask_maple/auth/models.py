#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: models.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-12-07 13:12:42 (CST)
# Last Update:星期三 2016-12-7 13:54:28 (CST)
#          By:
# Description:
# **************************************************************************
from flask_maple.models import db
from flask_maple.permission.models import Group
from datetime import datetime
from werkzeug.security import (generate_password_hash, check_password_hash)

group_user = db.Table(
    'group_user',
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')))


class UserMixin(object):
    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return str(self.id)
        except AttributeError:
            raise NotImplementedError('No `id` attribute - override `get_id`')

    def __eq__(self, other):
        '''
        Checks the equality of two `UserMixin` objects using `get_id`.
        '''
        if isinstance(other, UserMixin):
            return self.get_id() == other.get_id()
        return NotImplemented

    def __ne__(self, other):
        '''
        Checks the inequality of two `UserMixin` objects using `get_id`.
        '''
        equal = self.__eq__(other)
        if equal is NotImplemented:
            return NotImplemented
        return not equal


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(49), unique=True)
    email = db.Column(db.String(81), unique=True)
    password = db.Column(db.String(81), nullable=False)
    is_superuser = db.Column(db.Boolean, default=False)
    is_confirmed = db.Column(db.Boolean, default=False)
    register_time = db.Column(db.DateTime, default=datetime.now())
    last_login = db.Column(db.DateTime, nullable=True)
    groups = db.relationship(
        Group,
        secondary=group_user,
        lazy='joined',
        backref=db.backref(
            'users', lazy='joined'))

    def __str__(self):
        return self.username

    def __repr__(self):
        return '<User %r>' % self.username

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    def update_password(self, password):
        self.set_password(password)
        db.session.commit()


class AnonymousUser(object):
    id = None
    pk = None
    username = 'anonymous'
    is_active = False
    is_superuser = False

    def __str__(self):
        return self.username

    def __repr__(self):
        return '<AnonymousUser>'

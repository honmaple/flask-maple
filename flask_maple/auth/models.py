#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: models.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-12-07 13:12:42 (CST)
# Last Update:星期四 2017-5-11 12:9:28 (CST)
#          By:
# Description:
# **************************************************************************
from datetime import datetime
from sqlalchemy.ext.declarative import declared_attr

from flask_login import UserMixin as _UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from flask_maple.mail import MailMixin
from flask_maple.models import ModelMixin, db


class GroupMixin(object):
    @declared_attr
    def id(cls):
        return db.Column(db.Integer, primary_key=True)

    @declared_attr
    def name(cls):
        return db.Column(db.String(512), nullable=False, unique=True)

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
        return db.Column(db.DateTime, default=datetime.now())

    @declared_attr
    def last_login(cls):
        return db.Column(db.DateTime, default=datetime.now())

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    def __str__(self):
        return self.username

    def __repr__(self):
        return '<User %r>' % self.username

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: models.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-12-07 13:12:42 (CST)
# Last Update:星期三 2017-5-10 14:56:32 (CST)
#          By:
# Description:
# **************************************************************************
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from flask_maple.mail import MailMixin
from flask_maple.models import ModelMixin, db

user_group = db.Table(
    'user_group', db.Column('group_id', db.Integer, db.ForeignKey('group.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')))


class Group(db.Model):
    __tablename__ = 'group'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(512), nullable=False, unique=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Group %r>' % self.name


class User(db.Model, UserMixin, MailMixin, ModelMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(512), unique=True)
    email = db.Column(db.String(512), unique=True)
    password = db.Column(db.String(512), nullable=False)
    is_superuser = db.Column(db.Boolean, default=False)
    is_confirmed = db.Column(db.Boolean, default=False)
    register_time = db.Column(db.DateTime, default=datetime.now())
    last_login = db.Column(db.DateTime, default=datetime.now())
    groups = db.relationship(
        Group,
        secondary=user_group,
        lazy='dynamic',
        backref=db.backref(
            'users', lazy='dynamic'))

    def __str__(self):
        return self.username

    def __repr__(self):
        return '<User %r>' % self.username

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

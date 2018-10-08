#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: test.py
# Author: jianglin
# Email: mail@honmaple.com
# Created: 2017-12-11 15:42:30 (CST)
# Last Update: Wednesday 2018-09-26 10:52:52 (CST)
#          By:
# Description:
# **************************************************************************
import unittest
from main import app, db
from main import User, Group


class TestBase(unittest.TestCase):
    def setUp(self):
        class TestConfig(object):
            SQLALCHEMY_DATABASE_URI = 'sqlite://'
            DEBUG = True
            TESTING = True

        app.config.from_object(TestConfig())

        self.app = app

        with self.app.test_request_context():
            db.create_all()
            raw_users = [
                {
                    'username': 'user1',
                    'email': 'user1@example.com',
                    'password': 'user1'
                }, {
                    'username': 'user2',
                    'email': 'user2@example.com',
                    'password': 'user2'
                }, {
                    'username': 'user3',
                    'email': 'user3@example.com',
                    'password': 'user3'
                }
            ]
            raw_groups = [
                {
                    'name': 'group1'
                }, {
                    'name': 'group2'
                }, {
                    'name': 'group3'
                }
            ]
            for user in raw_users:
                password = user.pop('password')
                user = User(**user)
                user.set_password(password)
                user.save()

            for group in raw_groups:
                Group(**group).save()

    def tearDown(self):
        with self.app.test_request_context():
            db.drop_all()
            db.metadata.clear()

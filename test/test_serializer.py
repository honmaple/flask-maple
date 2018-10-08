#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: test_serializer.py
# Author: jianglin
# Email: mail@honmaple.com
# Created: 2017-12-25 16:17:40 (CST)
# Last Update: Wednesday 2018-09-26 10:52:52 (CST)
#          By:
# Description:
# **************************************************************************
import unittest
from main import User, Group
from test import TestBase


class SeTest(TestBase):
    def test_serializer(self):
        users = {}
        groups = {}
        with self.app.test_request_context():
            for user in User.query.all():
                users[user.username] = user

            for group in Group.query.all():
                groups[group.name] = group

            user = users['user1']
            columns = ['id', 'username', 'email', 'password', 'is_superuser',
                       'is_confirmed', 'register_time', 'last_login']
            related_columns = ['groups', 'permissions']
            result = {}
            for i in columns:
                result[i] = getattr(user, i)
            for i in related_columns:
                result[i] = getattr(user, i).all()
            self.assertEqual(user.to_json(), result)

            include = ['username', 'password']
            self.assertEqual(
                user.to_json(include=include), {
                    i: getattr(user, i)
                    for i in include
                })

            exclude = ['username', 'password']
            self.assertEqual(
                user.to_json(exclude=exclude), {
                    i: v
                    for i, v in result.items() if i not in exclude
                })


if __name__ == '__main__':
    unittest.main()

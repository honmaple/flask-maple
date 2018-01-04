#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: test_permission.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-12-25 11:23:20 (CST)
# Last Update:星期五 2018-01-05 00:40:54 (CST)
#          By:
# Description:
# **************************************************************************
import unittest
from main import User, Group, Permission
from test import TestBase


class PermTest(TestBase):
    def test_user_permission(self):
        users = {}
        groups = {}
        with self.app.test_request_context():
            for user in User.query.all():
                users[user.username] = user

            for group in Group.query.all():
                groups[group.name] = group

            def test_perm(identity):
                identity.add_perm('get', 'user.item')
                self.assertTrue(identity.has_perm('get', 'user.item'))

                self.assertFalse(identity.has_perm('get', 'user'))
                identity.add_perm('get', 'user')
                self.assertTrue(identity.has_perm('get', 'user'))

                self.assertTrue(
                    identity.has_perm('get', ['user', 'user.item']))

                identity.remove_perm('get', 'user')
                self.assertFalse(identity.has_perm('get', 'user'))

                self.assertFalse(
                    identity.has_perm(
                        'get', ['user', 'user.item'], and_=True))
                self.assertTrue(
                    identity.has_perm(
                        'get', ['user', 'user.item'], and_=False))

                self.assertTrue(
                    identity.has_perm(
                        'get', ['user.item', 'group'], and_=False))
                self.assertFalse(
                    identity.has_perm(
                        'get', ['user.item', 'group'], and_=True))

            user = users['user1']
            test_perm(user)
            group = groups['group1']
            test_perm(group)

            for p in Permission.query.all():
                p.delete()

            group.add_perm('get', 'user.item')
            self.assertFalse(user.has_perm('get', 'user.item'))
            group.users.append(user)
            self.assertTrue(user.has_perm('get', 'user.item'))

            group.users.remove(user)
            self.assertFalse(user.has_perm('get', 'user.item'))

            group2 = groups['group2']
            group.child_groups.append(group2)
            group2.add_perm('post', 'user')
            self.assertTrue(group2.has_perm('post', 'user'))
            self.assertTrue(group.has_perm('post', 'user'))

            group2.remove_perm('post', 'user')
            self.assertFalse(group2.has_perm('post', 'user'))
            self.assertFalse(group.has_perm('post', 'user'))


if __name__ == '__main__':
    unittest.main()

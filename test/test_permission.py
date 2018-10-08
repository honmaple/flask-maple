#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: test_permission.py
# Author: jianglin
# Email: mail@honmaple.com
# Created: 2017-12-25 11:23:20 (CST)
# Last Update: Monday 2018-10-08 17:10:28 (CST)
#          By:
# Description:
# **************************************************************************
import unittest
from main import User, Group
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

                identity.add_perm('post', 'user.item')
                self.assertTrue(
                    identity.has_perm(['get', 'post'], 'user.item'))
                self.assertFalse(
                    identity.has_perm(['get', 'post', 'delete'], 'user.item'))
                self.assertTrue(
                    identity.has_perm(
                        ['get', 'post', 'delete'], 'user.item', and_=False))

                self.assertFalse(identity.has_perm('get', 'user'))
                identity.add_perm('get', 'user')
                self.assertTrue(identity.has_perm('get', 'user'))

                self.assertTrue(
                    identity.has_perm('get', ['user', 'user.item']))

                identity.remove_perm('get', 'user')
                self.assertFalse(identity.has_perm('get', 'user'))

                self.assertFalse(
                    identity.has_perm('get', ['user', 'user.item']))
                self.assertTrue(
                    identity.has_perm(
                        'get', ['user', 'user.item'], res_and_=False))

                self.assertTrue(
                    identity.has_perm(
                        'get', ['user.item', 'group'], res_and_=False))
                self.assertFalse(
                    identity.has_perm(
                        'get', ['user.item', 'group'], res_and_=True))

            user = users['user1']
            test_perm(user)
            group = groups['group1']
            test_perm(group)

            user.__class__.permissions.property.mapper.class_.query.delete()
            group.__class__.permissions.property.mapper.class_.query.delete()

            group.add_perm('get', 'user.item')
            self.assertFalse(user.has_perm('get', 'user.item'))
            group.users.append(user)
            self.assertTrue(user.has_perm('get', 'user.item'))
            self.assertFalse(
                user.has_perm('get', 'user.item', ignore_group=True))

            group.users.remove(user)
            self.assertFalse(user.has_perm('get', 'user.item'))

            group2 = groups['group2']
            group.child_groups.append(group2)
            self.assertTrue(group2.has_perm('get', 'user.item'))
            group2.add_perm('post', 'user')
            self.assertFalse(group2.has_perm('post', 'user'))
            self.assertTrue(group2.has_perm('post', 'user', default=True))
            group.add_perm('post', 'user')
            self.assertTrue(group.has_perm('post', 'user'))
            self.assertTrue(group2.has_perm('post', 'user'))

            group2.remove_perm('post', 'user')
            self.assertFalse(group2.has_perm('post', 'user'))

            group2.remove_perm('post', 'user', reset=True)
            self.assertTrue(group2.has_perm('post', 'user'))

            group2.add_perm('post', 'user')
            group.remove_perm('post', 'user')
            self.assertFalse(group2.has_perm('post', 'user'))
            self.assertTrue(group2.has_perm('post', 'user', ignore_group=True))


if __name__ == '__main__':
    unittest.main()

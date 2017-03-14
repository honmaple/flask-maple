#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: redis.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-10-28 23:16:14 (CST)
# Last Update:星期二 2017-3-14 21:17:34 (CST)
#          By:
# Description:
# **************************************************************************
from redis import StrictRedis


class Redis(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        config = app.config['REDIS']
        self._redis_client = StrictRedis(**config)

    def __getattr__(self, name):
        return getattr(self._redis_client, name)

    def __getitem__(self, name):
        return self._redis_client[name]

    def __setitem__(self, name, value):
        self._redis_client[name] = value

    def __delitem__(self, name):
        del self._redis_client[name]

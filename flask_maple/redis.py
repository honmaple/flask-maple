#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: redis.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-10-28 23:16:14 (CST)
# Last Update: 星期五 2018-02-23 11:41:04 (CST)
#          By:
# Description:
# **************************************************************************
try:
    from rediscluster import StrictRedisCluster as StrictRedis
except ImportError:
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

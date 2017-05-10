#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: redis.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-10-28 23:16:14 (CST)
# Last Update:星期三 2017-5-10 14:34:1 (CST)
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

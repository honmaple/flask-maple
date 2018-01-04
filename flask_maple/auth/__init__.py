#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: __init__.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-12-07 14:04:22 (CST)
# Last Update:星期五 2018-01-05 00:19:49 (CST)
#          By:
# Description:
# **************************************************************************


def init_app(app):
    from .views import Auth
    Auth(app)

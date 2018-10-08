#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: __init__.py
# Author: jianglin
# Email: mail@honmaple.com
# Created: 2016-12-07 14:04:22 (CST)
# Last Update: Wednesday 2018-09-26 10:52:50 (CST)
#          By:
# Description:
# **************************************************************************


def init_app(app):
    from .views import Auth
    Auth(app)

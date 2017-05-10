#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: views.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-10-28 19:56:36 (CST)
# Last Update:星期三 2017-5-10 14:41:40 (CST)
#          By:
# Description:
# **************************************************************************
from flask import request, current_app, abort
from flask.views import MethodView
from flask_login import login_required, current_user
from functools import wraps


def is_admin(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user.is_authenticated and current_user.is_superuser:
            return func(*args, **kwargs)
        abort(403)

    return decorated_view


class BaseMethodView(MethodView):
    @property
    def page_info(self):
        page = request.args.get('page', 1, type=int)
        if hasattr(self, 'per_page'):
            per_page = getattr(self, 'per_page')
        else:
            per_page = current_app.config.setdefault('PER_PAGE', 20)

        number = request.args.get('number', per_page, type=int)
        if number > 100:
            number = per_page
        return page, number


class IsAuthMethodView(BaseMethodView):
    decorators = [login_required]


class IsAdminMethodView(BaseMethodView):
    decorators = [is_admin, login_required]

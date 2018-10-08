#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: form.py
# Author: jianglin
# Email: mail@honmaple.com
# Created: 2017-03-17 22:37:34 (CST)
# Last Update: Monday 2018-10-08 17:48:17 (CST)
#          By:
# Description:
# **************************************************************************
from flask import flash
from flask_maple.response import HTTP
from functools import wraps


def form_validate(form_class, success=None, error=None, f=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            form = form_class()
            if form.validate_on_submit():
                return func(*args, **kwargs)
            elif form.errors:
                if f is not None:
                    if callable(f):
                        flash(f())
                    elif f == '':
                        flash_errors(form)
                    else:
                        flash(f)
                if error is not None:
                    return error()
                return return_errors(form)
            if success is not None:
                return success()
            return HTTP.OK()

        return wrapper

    return decorator


def flash_errors(form):
    for field, errors in form.errors.items():
        flash(u"%s %s" % (getattr(form, field).label.text, errors[0]))
        break


def return_errors(form):
    for field, errors in form.errors.items():
        data = (u"%s %s" % (getattr(form, field).label.text, errors[0]))
        break
    return HTTP.BAD_REQUEST(message="form validate fail.", data=data)

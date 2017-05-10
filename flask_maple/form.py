#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: form.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-03-17 22:37:34 (CST)
# Last Update:星期三 2017-5-10 16:28:25 (CST)
#          By:
# Description:
# **************************************************************************
from flask import flash
from flask_maple.response import HTTPResponse
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
            return HTTPResponse(HTTPResponse.NORMAL_STATUS).to_response()

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
    return HTTPResponse(
        HTTPResponse.FORM_VALIDATE_ERROR, description=data).to_response()

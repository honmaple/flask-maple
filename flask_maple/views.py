#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: views.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-10-28 19:56:36 (CST)
# Last Update:星期四 2016-12-15 21:49:27 (CST)
#          By:
# Description:
# **************************************************************************
from flask.views import MethodView
from flask import (current_app, request, render_template)
from .response import HTTPResponse
from .utils import get_columns, get_model_columns
from .serializer import Serializer

__all__ = ['ViewList', 'View']


class BaseView(MethodView):
    model = None
    template = None
    serializer_kwargs = {}

    def get_page_info(self):
        page = request.args.get('page', 1, type=int)
        if hasattr(self, 'per_page'):
            per_page = getattr(self, 'per_page')
            number = request.args.get('number', per_page, type=int)
        else:
            per_page = current_app.config.setdefault('PER_PAGE', 20)
            number = request.args.get('number', per_page, type=int)
        if number > 100:
            number = current_app.config['PER_PAGE']
        return page, number

    @property
    def filter_dict(self):
        columns = get_columns(self.model)
        f = {}
        for k, v in columns.items():
            value = request.args.get(v)
            if value is not None:
                f[k] = value
        return f

    @property
    def sort_tuple(self):
        orderby = request.args.get('orderby')
        if orderby:
            orderby = orderby.split(',')
            columns = get_model_columns(self.model)
            return tuple(set(orderby) & set(columns))
        return tuple()

    def get_render_info(self, data):
        return data


class ViewList(BaseView):
    def __init__(self, model):
        self.model = model

    def get(self):
        page, number = self.get_page_info()
        filter_dict = self.filter_dict
        sort_tuple = self.sort_tuple
        if not isinstance(filter_dict, dict):
            return filter_dict
        if not isinstance(sort_tuple, tuple):
            return sort_tuple
        datalist = self.model.get_list(page, number, filter_dict, sort_tuple)
        print(datalist.items)
        serializer = Serializer(datalist, **self.serializer_kwargs)
        if self.template is None:
            return HTTPResponse(HTTPResponse.NORMAL_STATUS,
                                **serializer.data).to_response()
        data = self.get_render_info(**serializer.data)
        return render_template(self.template, **data)


class View(MethodView):
    model = None
    template = None
    serializer_kwargs = {}

    def get(self, *args, **kwargs):
        serializer = Serializer(
            self.model.get(kwargs), **self.serializer_kwargs)
        data = serializer.data
        if self.template is None:
            return HTTPResponse(
                HTTPResponse.NORMAL_STATUS, data=data).to_response()
        return render_template(self.template, **serializer.data)

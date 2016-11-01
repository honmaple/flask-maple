#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: views.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-10-28 19:56:36 (CST)
# Last Update:星期五 2016-10-28 19:56:38 (CST)
#          By:
# Description:
# **************************************************************************
from flask.views import MethodView
from flask import (current_app, request, render_template)
from .response import HTTPResponse

__all__ = ['ViewList', 'View']


class BaseView(MethodView):
    model = None
    form = None
    filter_dict = {}
    sort_tuple = ()
    template = None
    serializer = None
    validator = None

    @classmethod
    def get_filter_dict(cls):
        filter_dict = {}
        for k, v in cls.filter_dict:
            v = request.args.get(v)
            if v is not None:
                filter_dict.update(k=v)
        return filter_dict

    @classmethod
    def get_sort_tuple(cls):
        sort_tuple = ()
        return sort_tuple


class ViewList(BaseView):
    def get(self):
        filter_dict = self.get_filter_dict()
        sort_tuple = self.get_sort_tuple()
        if not isinstance(filter_dict, (dict, )):
            return filter_dict
        if not isinstance(sort_tuple, (tuple, )):
            return sort_tuple
        page = request.args.get('page', 1, type=int)
        if hasattr(self, 'per_page'):
            number = request.args.get('number',
                                      getattr(self, 'per_page'),
                                      type=int)
        else:
            number = request.args.get('number',
                                      current_app.config['PER_PAGE'],
                                      type=int)
        if number > 100:
            number = current_app.config['PER_PAGE']
        datalist = self.model.query.filter_by(**filter_dict).order_by(
            *sort_tuple).paginate(page, number, True)
        if self.template is None:
            serializer = self.serializer(datalist.items, many=True)
            data = serializer.data
            return HTTPResponse(
                HTTPResponse.NORMAL_STATUS, data=data).to_response()
        return render_template(self.template, data=datalist)


class View(BaseView):
    def get(self, pk):
        serializer = self.serializer(self.model.get(pk))
        if self.template is None:
            data = serializer.data
            return HTTPResponse(
                HTTPResponse.NORMAL_STATUS, data=data).to_response()
        else:
            return render_template(self.template, **data)

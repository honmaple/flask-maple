#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: views.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-10-28 19:56:36 (CST)
# Last Update:星期六 2016-11-19 22:21:30 (CST)
#          By:
# Description:
# **************************************************************************
from flask.views import MethodView
from flask import (current_app, request, render_template)
from .response import HTTPResponse

__all__ = ['ViewList', 'View']


class BaseView(MethodView):
    model = None
    template = None
    serializer = None

    def get_page_info(self):
        page = request.args.get('page', 1, type=int)
        if hasattr(self, 'per_page'):
            per_page = getattr(self, 'per_page')
            number = request.args.get('number',
                                      per_page,
                                      type=int)
        else:
            per_page = current_app.config.setdefault('PER_PAGE', 20)
            number = request.args.get('number', per_page, type=int)
        if number > 100:
            number = current_app.config['PER_PAGE']
        return page, number

    def get_filter_dict(self):
        filter_dict = {}
        return filter_dict

    def get_sort_tuple(self):
        sort_tuple = ()
        return sort_tuple

    def get_render_info(self, data):
        return data


class ViewList(BaseView):
    def get(self):
        page, number = self.get_page_info()
        filter_dict = self.get_filter_dict()
        sort_tuple = self.get_sort_tuple()
        if not isinstance(filter_dict, (dict, )):
            return filter_dict
        if not isinstance(sort_tuple, (tuple, )):
            return sort_tuple
        datalist = self.model.get_list(page, number, filter_dict, sort_tuple)
        serializer = self.serializer(datalist, many=True)
        data, pageinfo = serializer.data
        if self.template is None:
            return HTTPResponse(
                HTTPResponse.NORMAL_STATUS, data=data,
                pageinfo=pageinfo).to_response()
        data = self.get_render_info({'data': data, 'pageinfo': pageinfo})
        return render_template(self.template, **data)


class View(BaseView):
    def get(self, pk):
        serializer = self.serializer(self.model.get(pk))
        data = serializer.data
        if self.template is None:
            return HTTPResponse(
                HTTPResponse.NORMAL_STATUS, data=data).to_response()
        return render_template(self.template, data=data)

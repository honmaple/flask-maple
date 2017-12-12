#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: views.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-10-28 19:56:36 (CST)
# Last Update:星期一 2017-12-11 16:30:12 (CST)
#          By:
# Description:
# **************************************************************************
from flask import request, current_app, abort, jsonify
from flask.views import MethodView as _MethodView
from flask_login import login_required, current_user
from functools import wraps
from .serializer import Column, Serializer, PageInfo
from .utils import get_one_object


def is_admin(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user.is_authenticated and current_user.is_superuser:
            return func(*args, **kwargs)
        abort(403)

    return decorated_view


class MethodView(_MethodView):
    per_page = 20

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


class IsAuthMethodView(MethodView):
    decorators = [login_required]


class IsAdminMethodView(MethodView):
    decorators = [is_admin, login_required]


class QuickApi(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

    def create_api(self, *args, **kwargs):
        quickview = QuickView(*args, **kwargs)
        url = quickview.url
        endpoint = quickview.endpoint
        self.app.add_url_rule(
            url,
            view_func=quickview.listview.as_view('{}.itemlist'.format(
                endpoint)))
        self.app.add_url_rule(
            '{}/<pk>'.format(url),
            view_func=quickview.view.as_view('{}.item'.format(endpoint)))


class QuickView(object):
    def __init__(self,
                 model,
                 router=dict(),
                 serializer=None,
                 alias=dict(),
                 pk='id'):
        '''
        alias = {
            "project__owner__username":"user",
            "user":"project__owner__username"
        }
        '''
        self.model = model
        self.router = router
        self.serializer = serializer or Serializer
        self.pk = pk
        self.alias = alias
        self.column = Column(model)

    def get_filter_params(self, params):
        alias = self.alias.get('get', {
            column.name: column.name
            for column in self.column.columns
        })
        return {
            alias[key]: value
            for key, value in params.items() if key in alias
        }

    def get_orderby_params(self, params):
        alias = self.alias.get('orderby', {
            column.name: column.name
            for column in self.column.columns
        })
        orderby = params.get('orderby', '').split(',')
        desc = params.get('desc', '1').ljust(len(orderby), '1')
        return ['-{}'.format(alias[order])
                if desc[orderby.index(order)] == '1' else alias[order]
                for order in orderby if order in alias]

    def get_instances(self, filter_params, orderby_params, page, number):
        return self.model.query.filter_by(
            **filter_params).order_by(*orderby_params).paginate(page, number)

    @property
    def listview(self):
        _self = self

        class ListView(MethodView):
            def get(self):
                query_dict = request.args.to_dict()
                page, number = self.page_info
                filter_params = _self.get_filter_params(query_dict)
                orderby_params = _self.get_orderby_params(query_dict)
                instances = _self.get_instances(filter_params, orderby_params,
                                                page, number)
                serializer = _self.serializer(instances)
                pageinfo = PageInfo(instances).as_dict()
                return jsonify(data=serializer.data, pageinfo=pageinfo)

            def post(self):
                print(request.json, request.values, request.data, request.form)
                post_data = request.form.to_dict()
                nullable_columns = _self.column.nullable_columns
                notnullable_columns = _self.column.notnullable_columns
                unique_columns = _self.column.unique_columns
                unique_params = {
                    column.name: post_data.pop(column.name)
                    for column in unique_columns
                }
                if unique_columns and _self.model.query.filter_by(
                        **unique_params).exists():
                    return jsonify(
                        msg='{} is exists'.format(','.join(unique_columns)))
                for column in notnullable_columns:
                    if column.name not in post_data:
                        return jsonify(
                            msg='{} is required'.format(column.name))
                params = {
                    column.name: post_data.pop(column.name)
                    for column in notnullable_columns
                }
                params.update(**{
                    column.name: post_data.pop(column.name)
                    for column in nullable_columns if column.name in post_data
                })
                instance = _self.model(**params)
                instance.save()
                serializer = _self.serializer(instance)
                return jsonify(data=serializer.data)

        return ListView

    @property
    def view(self):
        _self = self

        class View(MethodView):
            def get(self, pk):
                has_instance, response = get_one_object(_self.model, {
                    _self.pk: pk
                })
                if not has_instance:
                    return response
                instance = response
                serializer = _self.serializer(instance)
                return jsonify(data=serializer.data)

            def put(self, pk):
                post_data = request.json
                has_instance, response = get_one_object(_self.model, {
                    _self.pk: pk
                })
                if not has_instance:
                    return response
                instance = response
                for column in _self.column.columns:
                    _column = post_data.pop(column.name, None)
                    if _column:
                        setattr(instance, column.name, _column)
                instance.save()
                serializer = _self.serializer(instance)
                return jsonify(data=serializer.data)

            def delete(self, pk):
                has_instance, response = get_one_object(_self.model, {
                    _self.pk: pk
                })
                if not has_instance:
                    return response
                instance = response
                serializer = _self.serializer(instance)
                instance.delete()
                return jsonify(data=serializer.data)

        return View

    @property
    def endpoint(self):
        return self.router.get('endpoint', self.model.__table__.name)

    @property
    def url(self):
        prefix_url = self.router.get('prefix_url', '/api')
        return self.router.get('url', '{}/{}'.format(
            prefix_url, self.model.__table__.name))

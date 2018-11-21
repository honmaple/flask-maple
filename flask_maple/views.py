#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: views.py
# Author: jianglin
# Email: mail@honmaple.com
# Created: 2016-10-28 19:56:36 (CST)
# Last Update: Wednesday 2018-11-21 10:44:25 (CST)
#          By:
# Description:
# **************************************************************************
from flask import request, current_app, abort, jsonify
from flask.views import MethodView as _MethodView
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime
from .serializer import Column, Serializer, PageInfo
from flask_maple.response import HTTP


def is_admin(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user.is_authenticated and current_user.is_superuser:
            return func(*args, **kwargs)
        abort(403)

    return decorated_view


class MethodView(_MethodView):
    per_page = 20

    def __init__(self, quickview=None):
        self._self = quickview

    @property
    def pageinfo(self):
        page = request.args.get('page', 1, type=int)
        if hasattr(self, 'per_page'):
            per_page = getattr(self, 'per_page')
        else:
            per_page = current_app.config.setdefault('PER_PAGE', 20)

        number = request.args.get('number', per_page, type=int)
        if number > 100:
            number = per_page
        return page, number

    def _set_releation_columns(self, instance, post_data):
        _self = self._self
        relation_columns = _self.column.relation_columns
        to_one_columns = [
            column for column in relation_columns
            if column.direction.name.endswith('ONE')
        ]
        to_many_columns = [
            column for column in relation_columns
            if column.direction.name.endswith('MANY')
        ]
        for column in to_one_columns:
            relation_model = column.mapper.class_
            if column.key in post_data:
                relation_instance = relation_model.query.filter_by(
                    id=post_data[column.key]).first()
                if relation_instance:
                    setattr(instance, column.key, relation_instance)
        for column in to_many_columns:
            relation_model = column.mapper.class_
            if column.key in post_data:
                params_id = post_data[column.key].split(',')
                relation_instance = relation_model.query.filter_by(
                    id__in=params_id).all()
                if relation_instance:
                    setattr(instance, column.key, relation_instance)
        return instance


class ItemListView(MethodView):
    def get(self):
        _self = self._self
        query_dict = request.data
        page, number = self.pageinfo
        filter_params = _self.get_filter_params(query_dict)
        orderby_params = _self.get_orderby_params(query_dict)
        instances = _self.get_instances(filter_params, orderby_params, page,
                                        number)
        serializer = _self.serializer(instances)
        pageinfo = PageInfo(instances).as_dict()
        return HTTP.OK(data=serializer.data, pageinfo=pageinfo)

    def post(self):
        post_data = request.data
        nullable_columns = self._self.column.nullable_columns
        unique_columns = self._self.column.unique_columns
        notnullable_columns = self._self.column.notnullable_columns
        for column in notnullable_columns:
            if column.name not in post_data:
                return jsonify(msg='{} is required'.format(column.name))

        for column in unique_columns:
            name = column.name
            if self._self.model.query.filter_by(**{
                    name: post_data.get(name)
            }).exists():
                return jsonify(msg='{} is exists'.format(name))

        params = {
            column.name: post_data.get(column.name)
            for column in notnullable_columns
        }
        params.update(
            **{
                column.name: post_data.get(column.name)
                for column in nullable_columns if column.name in post_data
            })

        instance = self._self.model(**params)
        self._set_releation_columns(instance, post_data)
        instance.save()
        serializer = self._self.serializer(instance)
        return HTTP.OK(data=serializer.data)


class ItemView(MethodView):
    def get(self, pk):
        ins = self._self.model.query.filter_by(**{
            self._self.pk: pk
        }).get_or_404()
        serializer = self._self.serializer(ins)
        return HTTP.OK(data=serializer.data)

    def put(self, pk):
        post_data = request.data
        ins = self._self.model.query.filter_by(**{
            self._self.pk: pk
        }).get_or_404()
        needed_columns = set(self._self.column.columns) ^ set(
            self._self.column.primary_columns) ^ set(
                self._self.column.foreign_keys)
        datetime_columns = self._self.column.datetime_columns
        for column in needed_columns:
            param = post_data.pop(column.name, None)
            if param is not None:
                setattr(
                    ins, column.name,
                    datetime.strptime(param, '%Y-%m-%d %H:%M:%S')
                    if column in datetime_columns else param)
        self._set_releation_columns(ins, post_data)
        ins.save()
        serializer = self._self.serializer(ins)
        return HTTP.OK(data=serializer.data)

    def delete(self, pk):
        ins = self._self.model.query.filter_by(**{
            self._self.pk: pk
        }).get_or_404()
        serializer = self._self.serializer(ins)
        ins.delete()
        return HTTP.OK(data=serializer.data)


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
        itemlistview = quickview.itemlistview
        itemview = quickview.itemview

        self.app.add_url_rule(
            url,
            view_func=itemlistview.as_view('{}.itemlist'.format(endpoint),
                                           quickview))
        self.app.add_url_rule(
            '{}/<pk>'.format(url),
            view_func=itemview.as_view('{}.item'.format(endpoint), quickview))


class QuickView(object):
    def __init__(self,
                 model,
                 router=dict(),
                 serializer=None,
                 alias=dict(),
                 decorators=(),
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
        self.decorators = decorators
        self.column = Column(model)

    def get_filter_params(self, params):
        alias = self.alias.get(
            'get',
            {column.name: column.name
             for column in self.column.columns})
        return {
            alias[key]: value
            for key, value in params.items() if key in alias
        }

    def get_orderby_params(self, params):
        alias = self.alias.get(
            'orderby',
            {column.name: column.name
             for column in self.column.columns})
        orderby = params.get('orderby', '').split(',')
        desc = params.get('desc', '1').ljust(len(orderby), '1')
        return [
            '-{}'.format(alias[order])
            if desc[orderby.index(order)] == '1' else alias[order]
            for order in orderby if order in alias
        ]

    def get_instances(self, filter_params, orderby_params, page, number):
        return self.model.query.filter_by(
            **filter_params).order_by(*orderby_params).paginate(page, number)

    @property
    def itemlistview(self):
        class new(ItemListView):
            decorators = self.decorators

        return new

    @property
    def itemview(self):
        class new(ItemView):
            decorators = self.decorators

        return new

    @property
    def endpoint(self):
        return self.router.get('endpoint', self.model.__table__.name)

    @property
    def url(self):
        prefix_url = self.router.get('prefix_url', '/api')
        return self.router.get(
            'url', '{}/{}'.format(prefix_url, self.model.__table__.name))

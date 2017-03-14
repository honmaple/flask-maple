#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: serializer.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-10-28 19:52:57 (CST)
# Last Update:星期三 2017-1-25 22:16:9 (CST)
#          By:
# Description:
# **************************************************************************
from sqlalchemy import inspect
from sqlalchemy.orm.interfaces import (ONETOMANY, MANYTOMANY)


class SerializerData(dict):
    def __init__(self, *args, **kwargs):
        super(SerializerData, self).__init__(*args, **kwargs)
        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(SerializerData, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(SerializerData, self).__delitem__(key)
        del self.__dict__[key]


class Serializer(object):
    def __init__(self, instance, many=False, include=[], exclude=[], depth=2):
        self.instance = instance
        self.many = many
        self.depth = depth
        if hasattr(self, 'include'):
            self.include = include or self.include
        else:
            self.include = include
        if hasattr(self, 'exclude'):
            self.exclude = exclude or self.exclude
        else:
            self.exclude = exclude

    @property
    def data(self):
        if self.include and self.exclude:
            raise ValueError('include and exclude can\'t work together')
        if self.many:
            return self._serializerlist(self.instance, self.depth)
        return self._serializer(self.instance, self.depth)

    def _serializerlist(self, instances, depth):
        results = []
        for instance in instances:
            result = self._serializer(instance, depth)
            if result:
                results.append(result)
        return results

    def _serializer(self, instance, depth):
        result = {}
        if depth == 0:
            return result
        depth -= 1
        model_class = self.get_model_class(instance)
        inp = self.get_inspect(model_class)
        model_data = self._serializer_model(inp, instance, depth)
        relation_data = self._serializer_relation(inp, instance, depth)
        result.update(model_data)
        result.update(relation_data)
        return result

    def _serializer_model(self, inp, instance, depth):
        result = {}
        model_columns = self.get_model_columns(inp)
        for column in model_columns:
            result[column] = getattr(instance, column)
        return result

    def _serializer_relation(self, inp, instance, depth):
        result = {}
        relation_columns = self.get_relation_columns(inp)
        for relation in relation_columns:
            column = relation.key
            if relation.direction in [ONETOMANY, MANYTOMANY
                                      ] and relation.uselist:
                children = getattr(instance, column)
                if relation.lazy == 'dynamic':
                    children = children.all()
                if children:
                    result[column] = Serializer(
                        children,
                        many=True,
                        exclude=[relation.back_populates],
                        depth=depth).data
                else:
                    result[column] = []
            else:
                child = getattr(instance, column)
                if relation.lazy == 'dynamic':
                    child = child.first()
                if child:
                    result[column] = Serializer(
                        child,
                        many=False,
                        exclude=[relation.back_populates],
                        depth=depth).data
                else:
                    result[column] = {}
        return result

    def get_model_class(self, instance):
        return getattr(instance, '__class__')

    def get_inspect(self, model_class):
        return inspect(model_class)

    def get_model_columns(self, inp):
        if self.include:
            model_columns = [
                column.name for column in inp.columns
                if column.name in self.include
            ]
        elif self.exclude:
            model_columns = [
                column.name for column in inp.columns
                if column.name not in self.exclude
            ]
        else:
            model_columns = [column.name for column in inp.columns]

        return model_columns

    def get_relation_columns(self, inp):
        if self.include:
            relation_columns = [
                relation for relation in inp.relationships
                if relation.key in self.include
            ]
        elif self.exclude:
            relation_columns = [
                relation for relation in inp.relationships
                if relation.key not in self.exclude
            ]
        else:
            relation_columns = [relation for relation in inp.relationships]
        return relation_columns


class FlaskSerializer(Serializer):
    @property
    def data(self):
        if self.include and self.exclude:
            raise ValueError('include and exclude can\'t work together')
        if self.many:
            if isinstance(self.instance, list):
                return self._serializerlist(self.instance, self.depth)
            pageinfo = {
                'items': True,
                'pages': self.instance.pages,
                'has_prev': self.instance.has_prev,
                'page': self.instance.page,
                'has_next': self.instance.has_next,
                'iter_pages': list(
                    self.instance.iter_pages(
                        left_edge=1,
                        left_current=2,
                        right_current=3,
                        right_edge=1))
            }
            return {
                'data': self._serializerlist(self.instance.items, self.depth),
                'pageinfo': pageinfo
            }
        return self._serializer(self.instance, self.depth)

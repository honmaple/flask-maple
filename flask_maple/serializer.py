#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: serializer.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-10-28 19:52:57 (CST)
# Last Update:星期三 2016-12-7 17:35:2 (CST)
#          By:
# Description:
# **************************************************************************


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


from sqlalchemy import inspect
from sqlalchemy.orm.interfaces import (ONETOMANY, MANYTOMANY, MANYTOONE)


class Se(object):
    def __init__(self, instance, many=False, include=[], exclude=[], depth=2):
        self.instance = instance
        self.many = many
        self.include = include
        self.exclude = exclude
        self.depth = depth

    @property
    def data(self):
        self.serializer_data = {}
        if self.include and self.exclude:
            raise ValueError('include and exclude can\'t work together')
        if self.many:
            if isinstance(self.instance, list):
                return self._serializerlist(self.instance, self.depth)
            return self._serializerlist(self.instance.items, self.depth)
        return self._serializer(self.instance, self.depth)

    def _serializerlist(self, instances, depth=2):
        return [self._serializer(instance, depth) for instance in instances]

    def _serializer(self, instance, depth=2):
        _data = {}
        depth -= 1
        if depth == 0:
            return self.serializer_data
        model_class = self.get_model_class(instance)
        inp = self.get_inspect(model_class)
        model_data = self._serializer_model(inp, instance, depth)
        # relation_data = self._serializer_relation(inp, instance, depth)
        return model_data
        # for relation in relation_columns:
        #     column = relation.key
        #     if relation.direction in [ONETOMANY, MANYTOMANY]:
        #         children = getattr(instance, column)
        #         if relation.lazy == 'dynamic':
        #             children = getattr(children, 'all()')
        #         _data[column] = self._serializerlist(children)
        #     else:
        #         child = getattr(instance, column)
        #         if relation.lazy == 'dynamic':
        #             child = getattr(child, 'first()')
        #         _data[column] = self._serializer(child, depth)
        return _data

    def _serializer_model(self, inp, instance, depth):
        data = {}
        model_columns = self.get_model_columns(inp)
        for column in model_columns:
            data[column] = getattr(instance, column)
        return data

    def _serializer_relation(self, inp, instance, depth):
        data = {}
        relation_columns = self.get_relation_columns(inp)
        for relation in relation_columns:
            column = relation.key
            if relation.direction in [ONETOMANY, MANYTOMANY]:
                children = getattr(instance, column)
                if relation.lazy == 'dynamic':
                    children = getattr(children, 'all()')
                data[column] = self._serializerlist(children)
            else:
                child = getattr(instance, column)
                if relation.lazy == 'dynamic':
                    child = getattr(child, 'first()')
                data[column] = self._serializer(child, depth)
        return data

    def get_model_class(self, instance):
        return getattr(instance, '__class__')

    def get_inspect(self, model_class):
        return inspect(model_class)

    def get_columns(self, model_class):
        inp = self.get_inspect(model_class)
        model_columns = self.get_model_columns(inp)
        relation_columns = self.get_relation_columns(inp)
        columns = set(model_columns + relation_columns)
        if self.include and self.exclude:
            raise ValueError('include and exclude can\'t work together')
        elif self.include:
            columns = columns & set(self.include)
        elif self.exclude:
            columns = columns ^ set(self.exclude)
            model_columns = list(columns & set(model_columns))
            relation_columns = list(columns & set(relation_columns))
        return model_columns, relation_columns

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


class Serializer(object):
    def __init__(self, instance, many=False):
        self.instance = instance
        self.many = many
        meta = getattr(self, 'Meta')
        self.fields = getattr(meta, 'fields')
        self.model = getattr(meta, 'model')

    @property
    def data(self):
        if self.many:
            self.paginate = self.instance
            self.instance = self.instance.items
            return self._serializerlist()
        return self._serializer()

    def _has_child(self, serializer, instance, field):
        if hasattr(serializer, field):
            return self.child_init(serializer, instance, field)
        return getattr(instance, field)

    def _serializer(self):
        data = SerializerData()
        for field in self.fields:
            if not hasattr(self.model, field):
                raise ValueError('"{0}" field does not exist.'.format(field))
            data[field] = self._has_child(self, self.instance, field)
        return data

    def _serializerlist(self):
        datalist = []
        for instance in self.instance:
            data = SerializerData()
            for field in self.fields:
                if not hasattr(self.model, field):
                    raise ValueError('"{0}" field does not exist.'.format(
                        field))
                data[field] = self._has_child(self, instance, field)
                datalist.append(data)
                pageinfo = {
                    'items': True if datalist else False,
                    'pages': self.paginate.pages,
                    'has_prev': self.paginate.has_prev,
                    'page': self.paginate.page,
                    'has_next': self.paginate.has_next,
                    'iter_pages': list(
                        self.paginate.iter_pages(
                            left_edge=1,
                            left_current=2,
                            right_current=3,
                            right_edge=1))
                }
        return datalist, SerializerData(pageinfo)

    def child_init(self, serializer, instance, field):
        # 子序列
        child_serializer = getattr(serializer, field)
        child_meta = getattr(child_serializer, 'Meta')
        child_fields = getattr(child_meta, 'fields')
        child_instance = getattr(instance, field)
        if not isinstance(child_instance, (list, )):
            return self._child_serializer(child_serializer, child_instance,
                                          child_fields)
        return self._child_serializerlist(child_serializer, child_instance,
                                          child_fields)

    def _child_serializer(self, serializer, instance, fields):
        data = SerializerData()
        for field in fields:
            data[field] = self._has_child(serializer, instance, field)
        return data

    def _child_serializerlist(self, serializer, instances, fields):
        datalist = []
        for instance in instances:
            data = SerializerData()
            for field in fields:
                data[field] = self._has_child(serializer, instance, field)
                datalist.append(data)
        return datalist

    class Meta:
        model = None
        fields = []

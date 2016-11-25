#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: serializer.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-10-28 19:52:57 (CST)
# Last Update:星期二 2016-11-8 23:3:41 (CST)
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
            'iter_pages': list(self.paginate.iter_pages(left_edge=1,
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

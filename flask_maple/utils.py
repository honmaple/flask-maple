#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: utils.py
# Author: jianglin
# Email: mail@honmaple.com
# Created: 2016-12-07 13:16:28 (CST)
# Last Update: Wednesday 2018-11-21 10:44:41 (CST)
#          By:
# Description:
# **************************************************************************
import os
from sqlalchemy import inspect


def gen_secret_key(length):
    return os.urandom(length)


def get_model_columns(model_class):
    inp = inspect(model_class)
    return [column.name for column in inp.columns]


def get_relation_columns(model_class):
    inp = inspect(model_class)
    c = []
    for relation in inp.relationships:
        relation_inp = inspect(relation.mapper.class_)
        for column in relation_inp.columns:
            key = relation.key + '__' + column.name
            c.append(key)
    return c


def get_columns(model_class):
    model_columns = get_model_columns(model_class)
    relation_columns = get_relation_columns(model_class)
    model_columns.extend(relation_columns)
    return model_columns

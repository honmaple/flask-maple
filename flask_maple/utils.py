#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: utils.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-12-07 13:16:28 (CST)
# Last Update:星期六 2016-12-10 14:3:12 (CST)
#          By:
# Description:
# **************************************************************************
import os
from sqlalchemy import inspect
from sqlalchemy.orm.mapper import Mapper


def gen_secret_key(length):
    return os.urandom(length)


def get_model_columns(model_class):
    inp = inspect(model_class)
    return [column.name for column in inp.columns]


def get_relation_columns(model_class):
    inp = inspect(model_class)
    c = {}
    for relation in inp.relationships:
        argument = relation.argument
        if isinstance(argument, Mapper):
            argument = argument.class_
        relation_inp = inspect(argument)
        for column in relation_inp.columns:
            key = relation.key + '__' + column.name
            c[key] = key
    return c


def get_columns(model_class):
    inp = inspect(model_class)
    c = {}
    for column in inp.columns:
        key = column.name
        c[key] = key
    for relation in inp.relationships:
        argument = relation.argument
        if isinstance(argument, Mapper):
            argument = argument.class_
        relation_inp = inspect(argument)
        for column in relation_inp.columns:
            key = relation.key + '__' + column.name
            c[key] = key
    return c

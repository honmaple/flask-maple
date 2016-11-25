#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: json.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-11-12 15:03:53 (CST)
# Last Update:星期六 2016-11-12 15:4:49 (CST)
#          By:
# Description:
# **************************************************************************
from flask.json import JSONEncoder
from speaklater import is_lazy_string


class CustomJSONEncoder(JSONEncoder):
    """This class adds support for lazy translation texts to Flask's
    JSON encoder. This is necessary when flashing translated texts."""

    def default(self, obj):
        if is_lazy_string(obj):
            try:
                return unicode(obj)  # python 2
            except NameError:
                return str(obj)  # python 3
        return super(CustomJSONEncoder, self).default(obj)

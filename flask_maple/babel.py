#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: babel.py
# Author: jianglin
# Email: mail@honmaple.com
# Created: 2016-12-11 23:42:23 (CST)
# Last Update: Wednesday 2018-09-26 10:52:51 (CST)
#          By:
# Description:
# **************************************************************************
from flask_maple import translations


def init_app(app):
    default_translation = app.config.get('BABEL_TRANSLATION_DIRECTORIES',
                                         'translations').split(';')
    default_translation.append(translations.path)
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = ';'.join(default_translation)

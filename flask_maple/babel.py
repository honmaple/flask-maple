#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: babel.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-12-11 23:42:23 (CST)
# Last Update: Sunday 2018-03-11 16:10:27 (CST)
#          By:
# Description:
# **************************************************************************
from flask_maple import translations


def init_app(app):
    default_translation = app.config.get('BABEL_TRANSLATION_DIRECTORIES',
                                         'translations').split(';')
    default_translation.append(translations.path)
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = ';'.join(default_translation)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: logging.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-11-19 10:32:05 (CST)
# Last Update:星期六 2016-11-19 13:59:48 (CST)
#          By:
# Description:
# **************************************************************************
import logging
import logging.config
from flask import current_app
from werkzeug import import_string

DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'flask_maple.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'flask_maple.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'standard': {
            'format':
            '''
                Message type:       %(levelname)s
                Location:           %(pathname)s:%(lineno)d
                Module:             %(module)s
                Function:           %(funcName)s
                Time:               %(asctime)s
                Message:
                %(message)s
            '''
        }

    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'server': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}


class RequireDebugFalse(logging.Filter):

    def filter(self, record):
        return current_app.config['DEBUG'] is False


class RequireDebugTrue(logging.Filter):

    def filter(self, record):
        return current_app.config['DEBUG'] is True


class Logging(object):

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        logging_config = app.config.setdefault('LOGGING_CONFIG',
                                               'logging.config.dictConfig')
        logging_setting = app.config.setdefault('LOGGING', {})
        if logging_config:
            logging_config_func = import_string(logging_config)
            logging.config.dictConfig(DEFAULT_LOGGING)
            if logging_setting:
                logging_config_func(logging_setting)

    @property
    def default(self):
        return DEFAULT_LOGGING

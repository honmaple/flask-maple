#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016, 2017 jianglin
# File Name: log.py
# Author: jianglin
# Email: mail@honmaple.com
# Created: 2016-11-19 10:32:05 (CST)
# Last Update: Wednesday 2018-09-26 10:52:52 (CST)
#          By:
# Description:
# **************************************************************************
import logging
import logging.config
from logging import Formatter
from logging.handlers import SMTPHandler
from threading import Thread
from copy import deepcopy

DEFAULT_LOG = {
    'info': 'logs/info.log',
    'error': 'logs/error.log',
    'send_mail': False,
    'toaddrs': [],
    'subject': 'Your Application Failed',
    'formatter': '''
            Message type:       %(levelname)s
            Location:           %(pathname)s:%(lineno)d
            Module:             %(module)s
            Function:           %(funcName)s
            Time:               %(asctime)s

            Message:

            %(message)s
            '''
}


class ThreadedSMTPHandler(SMTPHandler):
    def emit(self, record):
        thread = Thread(target=SMTPHandler.emit, args=(self, record))
        thread.start()


class Logging(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        config = deepcopy(DEFAULT_LOG)
        config.update(**app.config.get('LOGGING', {}))
        formatter = Formatter(config['formatter'])
        info_file_handler = logging.handlers.RotatingFileHandler(
            config['info'], maxBytes=100000, backupCount=10)

        info_file_handler.setLevel(logging.INFO)
        info_file_handler.setFormatter(formatter)
        app.logger.addHandler(info_file_handler)

        error_file_handler = logging.handlers.RotatingFileHandler(
            config['error'], maxBytes=100000, backupCount=10)

        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(formatter)
        app.logger.addHandler(error_file_handler)

        if config['send_mail']:
            # get mail info from flask_mail extension
            mail_config = {
                'username': app.config['MAIL_USERNAME'],
                'password': app.config['MAIL_PASSWORD'],
                'server': app.config['MAIL_SERVER'],
                'port': app.config['MAIL_PORT'],
                'default_sender': app.config['MAIL_DEFAULT_SENDER']
            }

            credentials = (mail_config['username'], mail_config['password'])
            mailhost = (mail_config['server'], mail_config['port'])
            mail_handler = ThreadedSMTPHandler(
                secure=(),
                mailhost=mailhost,
                fromaddr=mail_config['default_sender'],
                toaddrs=config['toaddrs'],
                subject=config['subject'],
                credentials=credentials)

            mail_handler.setLevel(logging.ERROR)
            mail_handler.setFormatter(formatter)
            app.logger.addHandler(mail_handler)

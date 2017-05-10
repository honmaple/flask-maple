#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016, 2017 jianglin
# File Name: logging.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-11-19 10:32:05 (CST)
# Last Update:星期三 2017-5-10 16:16:54 (CST)
#          By:
# Description:
# **************************************************************************
import logging
import logging.config
import os
from logging import Formatter
from logging.handlers import SMTPHandler
from threading import Thread

DEFAULT_LOG = {
    'info': 'info.log',
    'error': 'error.log',
    'send_mail': False,
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
        config = app.config.get('LOGGING', DEFAULT_LOG)
        logs_folder = config['LOGGING_FOLDER']
        formatter = Formatter(
            config.get('formatter', DEFAULT_LOG['formatter']))
        info_log = os.path.join(logs_folder, config.get('info',
                                                        DEFAULT_LOG['info']))

        info_file_handler = logging.handlers.RotatingFileHandler(
            info_log, maxBytes=100000, backupCount=10)

        info_file_handler.setLevel(logging.INFO)
        info_file_handler.setFormatter(formatter)
        app.logger.addHandler(info_file_handler)

        error_log = os.path.join(logs_folder, config.get('error',
                                                         DEFAULT_LOG['error']))

        error_file_handler = logging.handlers.RotatingFileHandler(
            error_log, maxBytes=100000, backupCount=10)

        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(formatter)
        app.logger.addHandler(error_file_handler)

        if app.config.get('send_mail', DEFAULT_LOG['send_mail']):
            credentials = (config['MAIL_USERNAME'], config['MAIL_PASSWORD'])
            mailhost = (config['MAIL_SERVER'], config['MAIL_PORT'])
            mail_handler = ThreadedSMTPHandler(
                secure=(),
                mailhost=mailhost,
                fromaddr=config['MAIL_DEFAULT_SENDER'],
                toaddrs=config['MAIL_ADMIN'],
                subject=config.get('subject', DEFAULT_LOG['subject']),
                credentials=credentials)

            mail_handler.setLevel(logging.ERROR)
            mail_handler.setFormatter(formatter)
            app.logger.addHandler(mail_handler)

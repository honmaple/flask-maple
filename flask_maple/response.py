#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: response.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-10-28 19:53:26 (CST)
# Last Update:星期二 2017-12-12 17:59:05 (CST)
#          By:
# Description:
# **************************************************************************
from flask import jsonify
from .babel import gettext as _


class HTTPResponse(object):
    NORMAL_STATUS = '200'
    USER_IS_CONFIRMED = '305'
    FORM_VALIDATE_ERROR = '305'

    FORBIDDEN = '403'
    HTTP_PARA_ERROR = '401'
    HTTP_NOT_FOUNT = '404'

    STATUS_DESCRIPTION = {
        NORMAL_STATUS: 'normal',
        USER_IS_CONFIRMED:
        _('Your account has been confirmed,don\'t need again'),
        FORM_VALIDATE_ERROR: _('Form validate error'),
        FORBIDDEN: _('You have no permission!'),
        HTTP_PARA_ERROR: 'params error',
        HTTP_NOT_FOUNT: '404',
    }

    def __init__(self,
                 status='200',
                 message='',
                 data='',
                 description='',
                 pageinfo=''):
        self.status = status
        self.message = message or self.STATUS_DESCRIPTION.get(status)
        self.data = data
        self.description = description
        self.pageinfo = pageinfo

    def to_dict(self):
        response = {
            'status': self.status,
            'message': self.message,
            'data': self.data,
            'description': self.description,
        }
        if self.pageinfo:
            response.update(pageinfo=self.pageinfo.as_dict())
        return response

    def to_response(self):
        response = self.to_dict()
        return jsonify(response)

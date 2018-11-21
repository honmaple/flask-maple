#!/usr/bin/env python
# -*- coding=UTF-8 -*-
# *************************************************************************
#   Copyright © 2015 JiangLin. All rights reserved.
#   File Name: mail.py
#   Author:JiangLin
#   Mail:mail@honmaple.com
#   Created Time: 2015-11-27 21:59:02
# *************************************************************************
from flask_mail import Mail as _Mail
from flask_mail import Message
from threading import Thread
from itsdangerous import (URLSafeTimedSerializer, BadSignature,
                          SignatureExpired)
from flask import current_app
from .utils import gen_secret_key

mail = _Mail()


class Mail(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        mail.init_app(app)

    def send_async_email(self, msg):
        with self.app.app_context():
            mail.send(msg)

    def send_email(self, *args, **kwargs):
        msg = Message(*args, **kwargs)
        thr = Thread(target=self.send_async_email, args=[msg])
        thr.start()


class MailMixin(object):
    @classmethod
    def _token_serializer(cls, key=None, salt=None):
        config = current_app.config
        if key is None:
            key = config.setdefault('SECRET_KEY', gen_secret_key(24))
        if salt is None:
            salt = config.setdefault('SECRET_KEY_SALT', gen_secret_key(24))
        return URLSafeTimedSerializer(key, salt=salt)

    @property
    def email_token(self):
        serializer = self._token_serializer()
        token = serializer.dumps(self.email)
        return token

    @classmethod
    def check_email_token(cls, token, max_age=259200):
        serializer = cls._token_serializer()
        try:
            email = serializer.loads(token, max_age=max_age)
        except BadSignature:
            return False
        except SignatureExpired:
            return False
        user = cls.query.filter_by(email=email).first()
        if user is None:
            return False
        return user

    # def send_email(self, *args, **kwargs):
    #     kwargs.update(recipients=[self.email])
    #     mail.send_email(*args, **kwargs)

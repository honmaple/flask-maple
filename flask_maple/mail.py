#!/usr/bin/env python
# -*- coding=UTF-8 -*-
# *************************************************************************
#   Copyright © 2015 JiangLin. All rights reserved.
#   File Name: email.py
#   Author:JiangLin
#   Mail:xiyang0807@gmail.com
#   Created Time: 2015-11-27 21:59:02
# *************************************************************************
from flask_mail import Mail
from flask_mail import Message
from threading import Thread
from itsdangerous import (URLSafeTimedSerializer, BadSignature,
                          SignatureExpired)
from flask import current_app
from flask_maple.utils import gen_secret_key

mail = Mail()


class UserMailMixin(object):
    def send_async_email(self, msg):
        # app = current_app._get_current_object()
        # with app.app_context():
        mail.send(msg)

    def send_email(self,
                   subject='',
                   recipients=None,
                   body=None,
                   html=None,
                   **kwargs):
        if not isinstance(recipients, list):
            recipients = [recipients]
        msg = Message(subject=subject, recipients=recipients, html=html)
        thr = Thread(target=self.send_async_email, args=[msg])
        thr.start()

    @property
    def email_token(self):
        config = current_app.config
        secret_key = config.setdefault('SECRET_KEY', gen_secret_key(24))
        salt = config.setdefault('SECRET_KEY_SALT', gen_secret_key(24))
        serializer = URLSafeTimedSerializer(secret_key)
        token = serializer.dumps(self.email, salt=salt)
        return token

    @staticmethod
    def check_email_token(token, max_age=259200):
        config = current_app.config
        secret_key = config.setdefault('SECRET_KEY', gen_secret_key(24))
        salt = config.setdefault('SECURITY_PASSWORD_SALT', gen_secret_key(24))
        serializer = URLSafeTimedSerializer(secret_key)
        try:
            email = serializer.loads(token, salt=salt, max_age=max_age)
        except BadSignature:
            return False
        except SignatureExpired:
            return False
        return email

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: token.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-12-10 11:22:36 (CST)
# Last Update:星期六 2016-12-10 12:16:22 (CST)
#          By:
# Description:
# **************************************************************************
from itsdangerous import (URLSafeTimedSerializer, BadSignature,
                          SignatureExpired)
from flask import current_app
from flask_maple.utils import gen_secret_key


class Token(object):
    def token(self, email):
        config = current_app.config
        secret_key = config.setdefault('SECRET_KEY')
        salt = config.setdefault('SECURITY_PASSWORD_SALT')
        assert secret_key is not None
        assert salt is not None
        serializer = URLSafeTimedSerializer(secret_key)
        token = serializer.dumps(email, salt=salt)
        return token

    def check_token(self, token, max_age=3600):
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

token = Token()

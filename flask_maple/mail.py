#!/usr/bin/env python
# -*- coding=UTF-8 -*-
# *************************************************************************
#   Copyright © 2015 JiangLin. All rights reserved.
#   File Name: email.py
#   Author:JiangLin
#   Mail:xiyang0807@gmail.com
#   Created Time: 2015-11-27 21:59:02
# *************************************************************************
from flask_mail import Message
from threading import Thread
from itsdangerous import URLSafeTimedSerializer
from flask import current_app


class MapleMail(object):
    def __init__(self, app, mail):
        self.app = app
        self.mail = mail

    def send_async_email(self, app, msg):
        with app.app_context():
            self.mail.send(msg)

    def email_send(self, to, template, subject):
        msg = Message(subject, recipients=[to], html=template)
        thr = Thread(target=self.send_async_email, args=[self.app, msg])
        thr.start()

    def email_token(self, email):
        config = current_app.config
        serializer = URLSafeTimedSerializer(config['SECRET_KEY'])
        token = serializer.dumps(email, salt=config['SECURITY_PASSWORD_SALT'])
        return token

    def confirm_token(self, token, expiration=360):
        config = current_app.config
        serializer = URLSafeTimedSerializer(config['SECRET_KEY'])
        try:
            email = serializer.loads(token,
                                     salt=config['SECURITY_PASSWORD_SALT'],
                                     max_age=expiration)
        except:
            return False
        return email

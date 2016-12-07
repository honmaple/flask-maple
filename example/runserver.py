#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: runserver.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-12-07 12:59:40 (CST)
# Last Update:星期三 2016-12-7 22:40:10 (CST)
#          By:
# Description:
# **************************************************************************
from flask import Flask, render_template, request, abort
from flask import jsonify
from flask_maple.models import db
from flask_maple.auth.models import User


class Config(object):
    DEBUG = True
    SECRET_KEY = 'asdsad'
    SECURITY_PASSWORD_SALT = ''
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'

    MAIL_SERVER = ''
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = ""
    MAIL_PASSWORD = ""
    MAIL_DEFAULT_SENDER = ''


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    return app


app = create_app()
db.init_app(app)

from sqlalchemy import inspect
from flask_maple.serializer import Serializer


@app.route('/')
def index():
    from flask_maple.permission.models import Group
    # group = Group()
    # group.name = 'assdasdda啊as达'
    # db.session.add(group)
    # db.session.commit()
    # inp = inspect(Group)
    # print(inp.c)
    # for column in inp.columns:
    #     print(column.name)
    # for relation in inp.relationships:
    #     print(relation)
    #     print(type( relation.direction))
    #     print(relation.lazy)
    #     print(relation.key)
    #     # print(dir(relation))
    group = Group.query.paginate(1, 1, True)
    # group = Group.query.first()

    user = User.query.all()
    user = User.query.first()
    # print(user.__class__)
    # # sqlalchemy.orm.interfaces.MANYTOONE
    a = Serializer(group, many=True, depth=3, exclude=['groups']).data
    print(a)

    return jsonify(a=a)
    # return 'a'


if __name__ == '__main__':
    app.run()

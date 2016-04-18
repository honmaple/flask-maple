#!/usr/bin/env python
# -*- coding=UTF-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: views.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-04-18 15:25:41 (CST)
# Last Update: 星期一 2016-4-18 18:4:35 (CST)
#          By:
# Description:
# **************************************************************************
from flask import (render_template, Blueprint, redirect, url_for, flash,
                   request, current_app, session, abort, jsonify)
from .form import LoginForm
# from flask_login import (login_user,
#                          logout_user,
#                          current_user,
#                          login_required)
# from flask_principal import (Identity, AnonymousIdentity,
#                              identity_changed)
# from werkzeug.security import generate_password_hash
# from maple import redis_data, app, db
# from maple.main.permissions import guest_permission, time_permission
# from maple.email.email import email_token, email_send, confirm_token
# from maple.user.models import User, UserInfor, UserSetting, Role
# from maple.auth.forms import LoginForm, RegisterForm, ForgetPasswdForm
# from maple.forms.forms import return_errors
# from datetime import datetime

site = Blueprint('auth', __name__)


def login():
    error = None
    form = LoginForm()
    if form.validate_on_submit() and request.method == "POST":
        validate_code = session['validate_code']
        validate = form.captcha.data
        if validate.lower() != validate_code.lower():
            return jsonify(judge=False, error=u'验证码错误')
        else:
            name = form.name.data
            passwd = form.passwd.data
            remember = request.get_json()["remember"]
            user = User.load_by_name(name)
            if user and User.check_password(user.passwd, passwd):
                if remember:
                    session.permanent = True

                login_user(user, remember=remember)

                identity_changed.send(current_app._get_current_object(),
                                      identity=Identity(user.id))
                flash(u'你已成功登陆')
                return jsonify(judge=True, error=error)
            else:
                error = u'用户名或密码错误'
                return jsonify(judge=False, error=error)
    else:
        if form.errors:
            return return_errors(form)
        else:
            pass
        return render_template('auth/login.html', form=form, error=error)


@site.route('/logout')
def logout():
    return 'logout'


@site.route('/register')
def register():
    return 'register'


site.add_url_rule('/login', 'auth', login)

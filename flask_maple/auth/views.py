#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: views.py
# Author: jianglin
# Email: mail@honmaple.com
# Created: 2016-12-07 14:01:14 (CST)
# Last Update: Wednesday 2018-11-21 10:49:57 (CST)
#          By:
# Description:
# **************************************************************************
from functools import wraps
from random import sample
from string import ascii_letters, digits

from flask import (flash, redirect, render_template, request, url_for, session)
from flask.views import MethodView
from flask_login import current_user, login_required
from flask_babel import gettext as _
from flask_maple.serializer import Serializer
from flask_maple.models import db
from flask_maple.response import HTTP

User = db.Model._decl_class_registry['User']


def guest_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if current_user.is_authenticated:
            flash(_("You have logined in ,needn't login again"))
            return redirect('/')
        return func(*args, **kwargs)

    return decorator


def check_params(keys):
    def _check_params(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            length = {
                'username': lambda value: 4 <= len(value) <= 20,
                'password': lambda value: 4 <= len(value) <= 20,
            }
            babel = {
                'username': _("Username"),
                'password': _("Password"),
                'email': _("Email"),
                'captcha': _("Captcha")
            }
            keys.append('captcha')
            post_data = request.json
            for key in keys:
                if not post_data.get(key):
                    msg = _('The %(key)s is required', key=babel[key])
                    return HTTP.BAD_REQUEST(message=msg)
                if not length.get(key, lambda value: True)(post_data[key]):
                    msg = _(
                        "The %(key)s's length must be between 4 to 20 characters",
                        key=babel[key])
                    return HTTP.BAD_REQUEST(message=msg)
            captcha = post_data['captcha']
            if captcha.lower() != session.pop('captcha', '00000').lower():
                msg = _('The captcha is error')
                return HTTP.BAD_REQUEST(message=msg)
            return func(*args, **kwargs)

        return decorator

    return _check_params


class LoginView(MethodView):
    decorators = [guest_required]

    def get(self):
        return render_template('auth/login.html')

    @check_params(['username', 'password'])
    def post(self):
        post_data = request.json
        username = post_data['username']
        password = post_data['password']
        remember = post_data.pop('remember', True)
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            msg = _('Username or Password Error')
            return HTTP.BAD_REQUEST(message=msg)
        user.login(remember)
        serializer = user.serializer() if hasattr(
            user, 'serializer') else Serializer(
                user, depth=1)
        return HTTP.OK(data=serializer.data)


class LogoutView(MethodView):
    decorators = [login_required]

    def get(self):
        current_user.logout()
        return redirect(request.args.get('next') or '/')


class RegisterView(MethodView):
    def get(self):
        return render_template('auth/register.html')

    @check_params(['username', 'password', 'email'])
    def post(self):
        post_data = request.json
        username = post_data['username']
        password = post_data['password']
        email = post_data['email']
        if User.query.filter_by(email=email).exists():
            msg = _('The email has been registered')
            return HTTP.BAD_REQUEST(message=msg)
        if User.query.filter_by(username=username).exists():
            msg = _('The username has been registered')
            return HTTP.BAD_REQUEST(message=msg)
        user = User(username=username, email=email)
        user.set_password(password)
        user.save()
        user.login(True)
        self.send_email(user)
        flash(_('An email has been sent to your.Please receive'))
        serializer = user.serializer() if hasattr(
            user, 'serializer') else Serializer(
                user, depth=1)
        return HTTP.OK(data=serializer.data)

    def send_email(self, user):
        token = user.email_token
        confirm_url = url_for(
            'auth.confirm_token', token=token, _external=True)
        html = render_template('templet/email.html', confirm_url=confirm_url)
        subject = _("Please confirm  your email")
        user.send_email(html=html, subject=subject)


class ForgetView(MethodView):
    decorators = [guest_required]

    def get(self):
        return render_template('auth/forget.html')

    @check_params(['email'])
    def post(self):
        post_data = request.json
        email = post_data['email']
        user = User.query.filter_by(email=email).first()
        if not user:
            msg = _('The email is error')
            return HTTP.BAD_REQUEST(message=msg)
        password = ''.join(sample(ascii_letters + digits, 8))
        user.set_password(password)
        user.save()
        self.send_email(user, password)
        flash(
            _('An email has been sent to you.'
              'Please receive and update your password in time'))
        return HTTP.OK()

    def send_email(self, user, password):
        html = render_template('templet/forget.html', confirm_url=password)
        subject = "Please update your password in time"
        user.send_email(html=html, subject=subject)


class ConfirmView(MethodView):
    decorators = [login_required]

    def post(self):
        if current_user.is_confirmed:
            return HTTP.BAD_REQUEST(message=_("user has been confirmed."))
        self.send_email(current_user)
        return HTTP.OK(
            message=_('An email has been sent to your.Please receive'))

    def send_email(self, user):
        token = user.email_token
        confirm_url = url_for(
            'auth.confirm_token', token=token, _external=True)
        html = render_template('templet/email.html', confirm_url=confirm_url)
        subject = _("Please confirm  your email")
        user.send_email(html=html, subject=subject)


class ConfirmTokenView(MethodView):
    def get(self, token):
        user = User.check_email_token(token)
        if not user:
            msg = _('The confirm link has been out of time.'
                    'Please confirm your email again')
            flash(msg)
            return redirect('/')
        if user.is_confirmed:
            flash(_('The email has been confirmed. Please login.'))
            return redirect('auth.login')
        user.is_confirmed = True
        user.save()
        flash('You have confirmed your account. Thanks!')
        return redirect('/')


class Auth(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        login_view = LoginView.as_view('auth.login')
        logout_view = LogoutView.as_view('auth.logout')
        register_view = RegisterView.as_view('auth.register')
        forget_view = ForgetView.as_view('auth.forget')
        confirm_view = ConfirmView.as_view('auth.confirm')
        confirm_token_view = ConfirmTokenView.as_view('auth.confirm_token')
        app.add_url_rule('/login', view_func=login_view)
        app.add_url_rule('/logout', view_func=logout_view)
        app.add_url_rule('/register', view_func=register_view)
        app.add_url_rule('/forget', view_func=forget_view)
        app.add_url_rule('/confirm', view_func=confirm_view)
        app.add_url_rule('/confirm/<token>', view_func=confirm_token_view)

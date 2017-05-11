#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: views.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-12-07 14:01:14 (CST)
# Last Update:星期四 2017-5-11 12:17:45 (CST)
#          By:
# Description:
# **************************************************************************
from functools import wraps
from random import sample
from string import ascii_letters, digits

from flask import (current_app, flash, redirect, render_template, request,
                   session, url_for)
from flask.views import MethodView
from flask_login import current_user, login_required, login_user, logout_user
from flask_maple.babel import gettext as _
from flask_maple.form import return_errors
from flask_maple.models import db
from flask_maple.response import HTTPResponse
from flask_principal import AnonymousIdentity, Identity, identity_changed

from .forms import ForgetForm, LoginForm, RegisterForm

User = db.Model._decl_class_registry['User']


def login(user, remember):
    login_user(user, remember=remember)
    identity_changed.send(
        current_app._get_current_object(), identity=Identity(user.id))


def guest_permission(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if current_user.is_authenticated:
            flash(_("You have logined in ,needn't login again"))
            return redirect('/')
        return func(*args, **kwargs)

    return decorator


class LoginView(MethodView):
    decorators = [guest_permission]

    def get(self):
        data = {'form': LoginForm()}
        return render_template('auth/login.html', **data)

    def post(self):
        form = LoginForm()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            remember = True if request.json.get('remember') else False
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login(user, remember)
                return HTTPResponse(HTTPResponse.NORMAL_STATUS).to_response()
            msg = _('Username or Password Error')
            return HTTPResponse(
                HTTPResponse.HTTP_CODE_PARA_ERROR, message=msg).to_response()
        else:
            if form.errors:
                return return_errors(form)
            return render_template('auth/login.html', form=form)


class LogoutView(MethodView):
    decorators = [login_required]

    def get(self):
        logout_user()
        for key in ('identity.id', 'identity.auth_type'):
            session.pop(key, None)
        identity_changed.send(
            current_app._get_current_object(), identity=AnonymousIdentity())
        return redirect(request.args.get('next') or '/')


class RegisterView(MethodView):
    def get(self):
        form = RegisterForm()
        data = {'form': form}
        return render_template('auth/register.html', **data)

    def post(self):
        form = RegisterForm()
        if form.validate_on_submit():
            email = form.email.data
            username = form.username.data
            password = form.password.data
            if User.query.filter_by(email=email).exists():
                msg = _('The email has been registered')
                return HTTPResponse(
                    HTTPResponse.HTTP_CODE_PARA_ERROR,
                    message=msg).to_response()
            if User.query.filter_by(username=username).exists():
                msg = _('The username has been registered')
                return HTTPResponse(
                    HTTPResponse.HTTP_CODE_PARA_ERROR,
                    message=msg).to_response()
            user = User(username=username, email=email)
            user.set_password(password)
            user.save()
            login(user, True)
            self.register_email(user)
            flash(_('An email has been sent to your.Please receive'))
            return HTTPResponse(HTTPResponse.NORMAL_STATUS).to_response()
        else:
            if form.errors:
                return return_errors(form)
            return render_template('auth/register.html', form=form)

    def register_email(self, user):
        token = user.email_token
        confirm_url = url_for(
            'auth.confirm_token', token=token, _external=True)
        html = render_template('templet/email.html', confirm_url=confirm_url)
        subject = _("Please confirm  your email")
        user.send_email(html=html, subject=subject)


class ForgetView(MethodView):
    decorators = [guest_permission]

    def get(self):
        form = ForgetForm()
        data = {'form': form}
        return render_template('auth/forget.html', **data)

    def post(self):
        form = ForgetForm()
        if form.validate_on_submit():
            email = form.email.data
            user = User.query.filter_by(email=email).first()
            if not user:
                msg = _('The email is error')
                return HTTPResponse(
                    HTTPResponse.HTTP_CODE_PARA_ERROR,
                    message=msg).to_response()
            password = ''.join(sample(ascii_letters + digits, 8))
            user.set_password(password)
            user.save()
            self.send_email(user, password)
            flash(
                _('An email has been sent to you.'
                  'Please receive and update your password in time'))
            return HTTPResponse(HTTPResponse.NORMAL_STATUS).to_response()
        else:
            if form.errors:
                return return_errors(form)
            return render_template('auth/forget.html', form=form)

    def send_email(self, user, password):
        html = render_template('templet/forget.html', confirm_url=password)
        subject = "Please update your password in time"
        user.send_email(html=html, subject=subject)


class ConfirmView(MethodView):
    decorators = [login_required]

    def post(self):
        if current_user.is_confirmed:
            return HTTPResponse(HTTPResponse.USER_IS_CONFIRMED).to_response()
        self.send_email(current_user)
        return HTTPResponse(
            HTTPResponse.NORMAL_STATUS,
            description=_(
                'An email has been sent to your.Please receive')).to_response()

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
        self.app = app
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

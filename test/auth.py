#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: auth.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-11-01 20:32:54 (CST)
# Last Update:星期四 2017-12-07 18:07:41 (CST)
#          By:
# Description:
# **************************************************************************
from .forms import LoginForm, RegisterForm, ForgetForm, return_errors
from .mail import MapleMail
from flask import (request, session, jsonify, flash, render_template, url_for,
                   redirect, current_app)
from flask.views import MethodView
from flask_maple.babel import gettext as _
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime
from random import sample
from string import ascii_letters, digits
from functools import wraps
from .response import HTTPResponse


class LoginBaseView(MethodView):
    form = LoginForm
    user_model = None
    use_principal = False

    def get(self):
        data = {'form': self.form()}
        return render_template('auth/login.html', **data)

    def post(self):
        form = self.form()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            remember = form.password.data
            user = self.user_model.query.filter_by(username=username).first()
            if user is not None and user.check_password(password):
                if remember:
                    login_user(user, remember=True)
                else:
                    login_user(user)
                if self.use_principal:
                    from flask_principal import Identity, identity_changed
                    identity_changed.send(
                        current_app._get_current_object(),
                        identity=Identity(user.id))
                return HTTPResponse(HTTPResponse.NORMAL_STATUS).to_response()
            else:
                return HTTPResponse(
                    HTTPResponse.LOGIN_USER_OR_PASSWORD_ERROR).to_response()
        else:
            if form.errors:
                return return_errors(form)
        return render_template('auth/login.html', form=form)


class LogoutBaseView(MethodView):
    decorators = [login_required]
    use_principal = False

    def get(self):
        logout_user()
        if self.use_principal:
            from flask_principal import (AnonymousIdentity, identity_changed)
            for key in ('identity.id', 'identity.auth_type'):
                session.pop(key, None)
            identity_changed.send(
                current_app._get_current_object(),
                identity=AnonymousIdentity())
        return redirect(request.args.get('next') or '/')


class RegisterBaseView(MethodView):
    form = RegisterForm
    user_model = None
    use_principal = False
    mail = None

    def get(self):
        data = {'form': self.form()}
        return render_template('auth/register.html', **data)

    def post(self):
        form = self.form()
        if form.validate_on_submit():
            useremail = self.user_model.query.filter_by(
                email=form.email.data).first()
            username = self.user_model.query.filter_by(
                username=form.username.data).first()
            if username is not None:
                return HTTPResponse(
                    HTTPResponse.LOGIN_USERNAME_UNIQUE).to_response()
            elif useremail is not None:
                return HTTPResponse(
                    HTTPResponse.LOGIN_EMAIL_UNIQUE).to_response()
            else:
                user = self.register_models(form)
                login_user(user)
                if self.use_principal:
                    from flask_principal import Identity, identity_changed
                    identity_changed.send(
                        current_app._get_current_object(),
                        identity=Identity(user.id))
                self.register_email(user.email)
                flash(_('An email has been sent to your.Please receive'))
                return HTTPResponse(HTTPResponse.NORMAL_STATUS).to_response()
        else:
            if form.errors:
                return return_errors(form)
            return render_template('auth/register.html', form=form)

    def register_model(self, form):
        user = self.user_model()
        user.username = form.username.data
        user.password = user.set_password(form.password.data)
        user.email = form.email.data
        user.save()
        return user

    def register_email(self, email):
        token = self.mail.email_token(email)
        confirm_url = url_for('auth.confirm', token=token, _external=True)
        html = render_template('templet/email.html', confirm_url=confirm_url)
        subject = _("Please confirm  your email")
        self.mail.email_send(email, html, subject)


class ForgetBaseView(MethodView):
    form = ForgetForm
    user_model = None

    def get(self):
        data = {'form': self.form()}
        return render_template('auth/forget.html', **data)

    def post(self):
        form = self.form()
        if form.validate_on_submit():
            email = form.email.data
            user = self.user_model.query.filter_by(email=email).first()
            if user is not None:
                password = set_password()
                user.password = password
                user.save()
                self.forget_email(user.email, password)
                flash(
                    _('An email has been sent to you.\
                      Please receive and update your password in time'))
                return HTTPResponse(HTTPResponse.NORMAL_STATUS).to_response()
            else:
                return HTTPResponse(
                    HTTPResponse.FORGET_EMAIL_NOT_REGISTER).to_response()
        else:
            if form.errors:
                return return_errors(form)
            return render_template('auth/forget.html', form=form)

    def forget_email(self, email, password):
        html = render_template('templet/forget.html', confirm_url=password)
        subject = "Please update your password in time"
        self.mail.email_send(email, html, subject)


class ConfirmBaseView(MethodView):
    decorators = [login_required]

    def get(self):
        if current_user.is_confirmed:
            return HTTPResponse(HTTPResponse.USER_IS_CONFIRMED).to_response()
        else:
            self.register_email(current_user.email)
            self.email_models()
            return jsonify(
                judge=True,
                error=_('An email has been sent to your.Please receive'))

    def confirm_models(self, user):
        user.is_confirmed = True
        user.confirmed_time = datetime.now()
        self.db.session.commit()


class ConfirmTokenBaseView(MethodView):
    def get(self, token):
        email = self.mail.confirm_token(token)
        if not email:
            flash(
                _('The confirm link has been out of time.\
                   Please confirm your email again'))
            return redirect('/')
        user = self.User.query.filter_by(email=email).first()
        if user.is_confirmed:
            flash(_('The email has been confirmed. Please login.'))
            return redirect('/')
        else:
            self.confirm_models(user)
            flash('You have confirmed your account. Thanks!')
        return redirect('/')


def set_password():
    password = ''.join(sample(ascii_letters + digits, 8))
    return password


def guest_permission(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if current_user.is_authenticated:
            flash(_("You have logined in ,needn't login again"))
            return redirect('/')
        return func(*args, **kwargs)

    return decorator

#!/usr/bin/env python
# -*- coding=UTF-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: auth.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-04-24 20:03:48 (CST)
# Last Update:星期六 2016-11-5 19:51:36 (CST)
#          By: jianglin
# Description:
# **************************************************************************
from flask import (request, session, flash, render_template, url_for, redirect,
                   current_app)
from flask.views import MethodView
from flask_babelex import gettext as _
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime
from random import sample
from string import ascii_letters, digits
from functools import wraps
from .response import HTTPResponse
from .forms import LoginForm, RegisterForm, ForgetForm, return_errors


def guest_permission(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if current_user.is_authenticated:
            flash(_("You have logined in ,needn't login again"))
            return redirect('/')
        return func(*args, **kwargs)

    return decorator


class LoginBaseView(MethodView):
    decorators = [guest_permission]
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
            remember = request.get_json()['remember']
            user = self.user_model.query.filter_by(username=username).first()
            if user is not None and user.check_password(password):
                if remember:
                    login_user(user, remember=True)
                else:
                    login_user(user)
                self.principal(user)
                return HTTPResponse(HTTPResponse.NORMAL_STATUS).to_response()
            else:
                return HTTPResponse(
                    HTTPResponse.LOGIN_USER_OR_PASSWORD_ERROR).to_response()
        else:
            if form.errors:
                return return_errors(form)
        return render_template('auth/login.html', form=form)

    def principal(self, user):
        if self.use_principal:
            from flask_principal import Identity, identity_changed
            identity_changed.send(
                current_app._get_current_object(), identity=Identity(user.id))


class LogoutBaseView(MethodView):
    decorators = [login_required]
    use_principal = False

    def get(self):
        logout_user()
        self.principal()
        return redirect(request.args.get('next') or '/')

    def principal(self):
        if self.use_principal:
            from flask_principal import (AnonymousIdentity, identity_changed)
            for key in ('identity.id', 'identity.auth_type'):
                session.pop(key, None)
            identity_changed.send(
                current_app._get_current_object(),
                identity=AnonymousIdentity())


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
                self.principal(user)
                self.register_email(user.email)
                flash(_('An email has been sent to your.Please receive'))
                return HTTPResponse(HTTPResponse.NORMAL_STATUS).to_response()
        else:
            if form.errors:
                return return_errors(form)
            return render_template('auth/register.html', form=form)

    def principal(self, user):
        if self.use_principal:
            from flask_principal import Identity, identity_changed
            identity_changed.send(
                current_app._get_current_object(), identity=Identity(user.id))

    def register_model(self, form):
        user = self.user_model()
        user.username = form.username.data
        user.password = form.password.data
        user.email = form.email.data
        user.add()
        return user

    def register_email(self, email):
        token = self.mail.custom_email_token(email)
        confirm_url = url_for(
            'auth.confirm_token', token=token, _external=True)
        html = render_template('templet/email.html', confirm_url=confirm_url)
        subject = _("Please confirm  your email")
        self.mail.custom_email_send(email, html, subject)


class ForgetBaseView(MethodView):
    decorators = [guest_permission]
    form = ForgetForm
    user_model = None
    mail = None

    def get(self):
        data = {'form': self.form()}
        return render_template('auth/forget.html', **data)

    def post(self):
        form = self.form()
        if form.validate_on_submit():
            email = form.email.data
            user = self.user_model.query.filter_by(email=email).first()
            if user is not None:
                password = ''.join(sample(ascii_letters + digits, 8))
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
        self.mail.custom_email_send(email, html, subject)


class ConfirmBaseView(MethodView):
    decorators = [login_required]
    mail = None

    def post(self):
        if current_user.is_confirmed:
            return HTTPResponse(HTTPResponse.USER_IS_CONFIRMED).to_response()
        self.register_email(current_user.email)
        self.email_models()
        return HTTPResponse(
            HTTPResponse.NORMAL_STATUS,
            description=_(
                'An email has been sent to your.Please receive')).to_response()

    def email_models(self):
        current_user.send_email_time = datetime.now()
        current_user.save()

    def register_email(self, email):
        token = self.mail.custom_email_token(email)
        confirm_url = url_for(
            'auth.confirm_token', token=token, _external=True)
        html = render_template('templet/email.html', confirm_url=confirm_url)
        subject = _("Please confirm  your email")
        self.mail.custom_email_send(email, html, subject)


class ConfirmTokenBaseView(MethodView):
    user_model = None
    mail = None

    def get(self, token):
        email = self.mail.custom_confirm_token(token)
        if not email:
            msg = _('The confirm link has been out of time.\
                   Please confirm your email again')
            flash(msg)
            return redirect('/')
        user = self.user_model.query.filter_by(email=email).first()
        if user.is_confirmed:
            flash(_('The email has been confirmed. Please login.'))
            return redirect('auth.login')
        self.confirm_models(user)
        flash('You have confirmed your account. Thanks!')
        return redirect('/')

    def confirm_models(self, user):
        user.is_confirmed = True
        user.confirmed_time = datetime.now()
        user.save()


class Auth(object):
    def __init__(self,
                 app=None,
                 mail=None,
                 user_model=None,
                 use_principal=False):
        self.app = app
        self.mail = mail
        self.use_principal = use_principal
        self.user_model = user_model
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        login_view = self.login_view().as_view('auth.login')
        logout_view = self.logout_view().as_view('auth.logout')
        register_view = self.register_view().as_view('auth.register')
        forget_view = self.forget_view().as_view('auth.forget')
        confirm_view = self.confirm_view().as_view('auth.confirm')
        confirm_token_view = self.confirm_token_view().as_view(
            'auth.confirm_token')
        app.add_url_rule('/login', view_func=login_view)
        app.add_url_rule('/logout', view_func=logout_view)
        app.add_url_rule('/register', view_func=register_view)
        app.add_url_rule('/forget', view_func=forget_view)
        app.add_url_rule('/confirm', view_func=confirm_view)
        app.add_url_rule('/confirm/<token>', view_func=confirm_token_view)

    def login_view(self):
        class LoginView(LoginBaseView):
            user_model = self.user_model
            use_principal = True

        return LoginView

    def logout_view(self):
        class LogoutView(LogoutBaseView):
            use_principal = True

        return LogoutView

    def register_view(self):
        class RegisterView(RegisterBaseView):
            user_model = self.user_model
            mail = self.mail
            use_principal = True

        return RegisterView

    def forget_view(self):
        class ForgetView(ForgetBaseView):
            mail = self.mail
            user_model = self.user_model

        return ForgetView

    def confirm_view(self):
        class ConfirmView(ConfirmBaseView):
            mail = self.mail

        return ConfirmView

    def confirm_token_view(self):
        class ConfirmTokenView(ConfirmTokenBaseView):
            user_model = self.user_model
            mail = self.mail

        return ConfirmTokenView

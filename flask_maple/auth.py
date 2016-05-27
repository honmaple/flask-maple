#!/usr/bin/env python
# -*- coding=UTF-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: auth.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-04-24 20:03:48 (CST)
# Last Update:星期四 2016-5-19 15:30:40 (CST)
#          By: jianglin
# Description:
# **************************************************************************
from .forms import LoginForm, RegisterForm, ForgetPasswordForm, return_errors
from .mail import MapleMail
from flask import (request, session, jsonify, flash, render_template, url_for,
                   redirect, current_app, abort)
from werkzeug.security import generate_password_hash
from flask_babel import gettext as _
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime, timedelta
from random import sample
from string import ascii_letters, digits
from functools import wraps


def set_password():
    password = ''.join(sample(ascii_letters + digits, 8))
    password_hash = generate_password_hash(password)
    return password, password_hash


def guest_permission(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if current_user.is_authenticated:
            flash(_("You have logined in ,needn't login again"))
            return redirect('/')
        return func(*args, **kwargs)

    return decorator


def check_time(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if current_user.send_email_time is None:
            pass
        if datetime.now() < current_user.send_email_time + timedelta(
                seconds=360):
            return jsonify(judge=False,
                           error="Your confirm link have not out of time," +
                           "Please confirm your email in time")
        return func(*args, **kwargs)

    return decorator


class Auth(object):
    def __init__(self,
                 app=None,
                 db=None,
                 mail=None,
                 user_model=None,
                 use_principal=False,
                 login_form=LoginForm,
                 register_form=RegisterForm,
                 forget_form=ForgetPasswordForm):
        self.db = db
        self.mail = MapleMail(app=app, mail=mail)
        self.use_principal = use_principal
        self.User = user_model
        self.login_form = login_form
        self.register_form = register_form
        self.forget_form = forget_form
        if app is not None:
            self.app = app
            self.init_app(self.app)
        else:
            self.app = None

    def init_app(self, app):
        app.add_url_rule('/register',
                         'auth.register',
                         self.register,
                         methods=['GET', 'POST'])
        app.add_url_rule('/login',
                         'auth.login',
                         self.login,
                         methods=['GET', 'POST'])
        app.add_url_rule('/forget',
                         'auth.forget',
                         self.forget,
                         methods=['GET', 'POST'])
        app.add_url_rule('/confirm-email',
                         'auth.confirm_email',
                         self.confirm_email,
                         methods=['POST'])
        app.add_url_rule('/logout', 'auth.logout', self.logout)
        app.add_url_rule('/confirm/<token>', 'auth.confirm', self.confirm)

    @guest_permission
    def login(self):
        error = None
        form = self.login_form()
        if form.validate_on_submit() and request.method == "POST":
            username = form.username.data
            password = form.password.data
            remember = form.remember.data
            user = self.User.query.filter_by(username=username).first()
            if user is not None and user.check_password(password):
                if remember:
                    session.permanent = True
                login_user(user, remember=remember)
                self.principals(user)
                flash(_('You have logined in'))
                return jsonify(judge=True, error=error)
            else:
                error = _('Name or Password is error')
                return jsonify(judge=False, error=error)
        else:
            if form.errors:
                return return_errors(form)
            else:
                pass
            return render_template('auth/login.html', form=form, error=error)

    def logout(self):
        logout_user()
        if self.use_principal:
            from flask_principal import (AnonymousIdentity, identity_changed)
            for key in ('identity.id', 'identity.auth_type'):
                session.pop(key, None)
            identity_changed.send(current_app._get_current_object(),
                                  identity=AnonymousIdentity())
        return redirect(request.args.get('next') or '/')

    @guest_permission
    def register(self):
        error = None
        form = self.register_form()
        if form.validate_on_submit() and request.method == "POST":
            useremail = self.User.query.filter_by(
                email=form.email.data).first()
            username = self.User.query.filter_by(
                username=form.username.data).first()
            if username is not None:
                error = _('The name has been registered')
                return jsonify(judge=False, error=error)
            elif useremail is not None:
                error = _('The email has been registered')
                return jsonify(judge=False, error=error)
            else:
                user = self.register_models(form)
                login_user(user)
                self.principals(user)
                self.register_email(user.email)
                flash(_('An email has been sent to your.Please receive'))
                return jsonify(judge=True, error=error)
        else:
            if form.errors:
                return return_errors(form)
            else:
                pass
            return render_template('auth/register.html', form=form)

    def forget(self):
        error = None
        form = self.forget_form()
        if form.validate_on_submit() and request.method == "POST":
            user = self.User.query.filter_by(
                email=form.confirm_email.data).first()
            if user is not None:
                password, user.password = set_password()
                self.db.session.commit()
                self.forget_email(user.email, password)
                flash(_(
                    'An email has been sent to you.Please receive and update your password in time'))
                return jsonify(judge=True, error=error)
            else:
                error = _('The email is error')
                return jsonify(judge=False, error=error)
        else:
            if form.errors:
                return return_errors(form)
            else:
                pass
            return render_template('auth/forget.html', form=form)

    def confirm(self, token):
        email = self.mail.confirm_token(token)
        if not email:
            flash(_(
                'The confirm link has been out of time.Please confirm your email again'))
            return redirect('/')
        user = self.User.query.filter_by(email=email).first()
        if user.is_confirmed:
            flash(_('The email has been confirmed. Please login.'))
            return redirect('/')
        else:
            self.confirm_models(user)
            flash('You have confirmed your account. Thanks!')
        return redirect('/')

    @login_required
    @check_time
    def confirm_email(self):
        if current_user.is_confirmed:
            return jsonify(
                judge=False,
                error=_('Your account has been confirmed,don\'t need again'))
        else:
            self.register_email(current_user.email)
            self.email_models()
            return jsonify(
                judge=True,
                error=_('An email has been sent to your.Please receive'))

    def confirm_models(self, user):
        user.is_confirmed = True
        user.confirmed_time = datetime.now()
        user.roles = 'writer'
        self.db.session.commit()

    def email_models(self):
        current_user.send_email_time = datetime.now()
        self.db.session.commit()

    def register_models(self, form):
        user = self.User()
        user.username = form.username.data
        user.password = user.set_password(form.password.data)
        user.email = form.email.data
        self.db.session.add(user)
        self.db.session.commit()
        return user

    def register_email(self, email):
        token = self.mail.email_token(email)
        confirm_url = url_for('auth.confirm', token=token, _external=True)
        html = render_template('templet/email.html', confirm_url=confirm_url)
        subject = _("Please confirm  your email")
        self.mail.email_send(email, html, subject)

    def forget_email(self, email, password):
        html = render_template('templet/forget.html', confirm_url=password)
        subject = "Please update your password in time"
        self.mail.email_send(email, html, subject)

    def principals(self, user):
        if self.use_principal:
            from flask_principal import Identity, identity_changed
            identity_changed.send(current_app._get_current_object(),
                                  identity=Identity(user.id))
        else:
            pass

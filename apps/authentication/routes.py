# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import datetime
import requests

from flask import render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_user,
    logout_user
)
from apps import db, login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, CreateAccountForm, ChangePasswordForm, GetUserEmailForm
from apps.authentication.models import Users
from apps.authentication.util import verify_pass, hash_pass
from apps.home.emailstuff import sendEmail
from apps.home.dbquery import executeSQL, getValues
import secrets
from apps.home.helper import getTexts, getErrorMessage

@blueprint.route('/')
def route_default():
    return redirect(url_for('authentication_blueprint.login'))


# Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    texts = getTexts('login')
    if 'login' in request.form:

        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = Users.query.filter_by(username=username).first()

        # Check the password
        if user and verify_pass(password, user.password):

            login_user(user)
            return redirect(url_for('authentication_blueprint.route_default'))

        # Something (user or pass) is not ok
        texts['msg'] = getErrorMessage('userOrPwdIsWrong')
        return render_template('accounts/login.html',
                               form=login_form,
                               **texts)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form,
                               **texts
                               )

    return redirect(url_for('home_blueprint.index'))

@blueprint.route('/changepassword/<token>', methods=['GET','POST'])
def changepassword(token):
    texts = getTexts('changepassword')
    changepassword_form = ChangePasswordForm(request.form)
    if 'password' in request.form:
      #read form data
      password = request.form['password']
      confirm_password = request.form['confirm_password']
      if password == confirm_password:
            user = Users.query.filter_by(recoverEMailToken=token).first()
            user.password = hash_pass(password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('authentication_blueprint.login'))
      else:
          texts['msg'] = getErrorMessage('passwordsAreDifferent')
          return render_template('accounts/changepassword.html',
                                 form=changepassword_form,
                                 **texts)
    else:
        recoverEmailTimeStamp = getValues("select recoverEmailTimeStamp from Users "
                                          f"where recoverEMailToken = '{token}'")
        if (datetime.datetime.now() - recoverEmailTimeStamp).days > 1:
            get_user_email_form = GetUserEmailForm(request.form)
            texts['msg'] = getErrorMessage('passwordsAreDifferent')
            return render_template('accounts/getuseremail.html',
                                   form=get_user_email_form,
                                   **texts)
    return render_template('accounts/changepassword.html',
                           form=changepassword_form,
                           **texts)

@blueprint.route('/get_user_email', methods=['GET', 'POST'])
def get_user_email():
    texts = getTexts('getuseremail')
    get_user_email_form = GetUserEmailForm(request.form)
    if 'user_email' in request.form:
        toEMail = request.form['user_email']

        if getValues(f"select count(1) from Users where email = '{toEMail}'") != 1:
            texts['msg'] = getErrorMessage('emailNotRegistered')
            return render_template('accounts/getuseremail.html',
                                   form=get_user_email_form,
                                   **texts)
        token = secrets.token_urlsafe()
        ip = requests.get('https://checkip.amazonaws.com').text.strip()
        url = f"http://{ip}:50051{url_for('authentication_blueprint.changepassword',token=token)}"
        sendEmail(toEMail, 'emailChangePassword', {'url': url})
        executeSQL(f"update Users set recoverEmailToken = '{token}',"
                   f" recoverEmailTimeStamp = current_timestamp "
                   f"where email = '{toEMail}'")
        texts['msg'] = getErrorMessage('emailSent')
        return render_template('accounts/getuseremail.html',
                               form=get_user_email_form,
                               **texts)
    else:
        return render_template('accounts/getuseremail.html',
                               form=get_user_email_form,
                               **texts)

@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    texts = getTexts('register')
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username = request.form['username']
        email = request.form['email']

        # Check usename exists
        user = Users.query.filter_by(username=username).first()
        if user:
            texts['msg'] = getErrorMessage('userAlreadyRegistered')
            return render_template('accounts/register.html',
                                   success=False,
                                   form=create_account_form,
                                   **texts)

        # Check email exists
        user = Users.query.filter_by(email=email).first()
        if user:
            texts['msg'] = getErrorMessage('emailAlreadyRegistered')
            return render_template('accounts/register.html',
                                   success=False,
                                   form=create_account_form,
                                   **texts)

        # else we can create the user
        user = Users(**request.form)
        db.session.add(user)
        db.session.commit()

        return render_template('accounts/register.html',
                               msg=f'{texts["endOfRegister"]} <a href="/login">login!</a>',
                               success=True,
                               form=create_account_form,
                               **texts)

    else:
        return render_template('accounts/register.html',
                               form=create_account_form,
                               **texts)


@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.login'))


# Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500

# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import datetime

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

@blueprint.route('/')
def route_default():
    return redirect(url_for('authentication_blueprint.login'))


# Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
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
        return render_template('accounts/login.html',
                               msg= 'Usuário desconhecido ou senha incorreta',   #mgd Wrong user or password
                               form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form)

    return redirect(url_for('home_blueprint.index'))

@blueprint.route('/changepassword/<token>', methods=['GET','POST'])
def changepassword(token):
    changepassword_form = ChangePasswordForm(request.form)
    if 'password' in request.form:
      #read form data
      password = request.form['password']
      confirm_password = request.form['confirm_password']
      if password == confirm_password:
            login_form = LoginForm(request.form)
            user = Users.query.filter_by(recoverEMailToken=token).first()
            user.password = hash_pass(password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('authentication_blueprint.login'))
      else:
          return render_template('accounts/changepassword.html',
                                 msg='Senhas diferem. Por favor, redigite.',  # mgd Wrong user or password
                                 form=changepassword_form)
    else:
        recoverEmailTimeStamp = getValues("select recoverEmailTimeStamp from Users "
                                          f"where recoverEMailToken = '{token}'")
        if (datetime.datetime.now() - recoverEmailTimeStamp).days > 1:
            get_user_email_form = GetUserEmailForm(request.form)
            return render_template('accounts/getuseremail.html',
                                   msg='O link de recuperação de senhas está sendo usado fora do prazo.<br>'
                                       'Por favor, forneça o seu email novamente para receber o link atualizado.',
                                   form=get_user_email_form)
    return render_template('accounts/changepassword.html',
                           form=changepassword_form)

@blueprint.route('/get_user_email', methods=['GET', 'POST'])
def get_user_email():
    get_user_email_form = GetUserEmailForm(request.form)
    if 'user_email' in request.form:
        toEMail = request.form['user_email']

        if getValues(f"select count(1) from Users where email = '{toEMail}'") != 1:
            return render_template('accounts/getuseremail.html',
                                   msg='E-Mail não cadastrado.',
                                   form=get_user_email_form)
        token = secrets.token_urlsafe()
        url = f"{url_for('authentication_blueprint.changepassword',token=token)}"
        executeSQL(f"update Users set recoverEmailToken = '{token}',"
                   f" recoverEmailTimeStamp = current_timestamp "
                   f"where email = '{toEMail}'")
        sendEmail(toEMail, 'emailChangePassword', {'url': url})
        return render_template('accounts/getuseremail.html',
                                msg='Foi enviado um email para esse endereço com o link para atualização da sua senha.<br>'
                                    'Abra o email, clique no link e recadastre sua senha de acesso. Caso não veja esse email '
                                    'na sua Caixa de Entrada, procure na Lixeira da sua conta.<br>'
                                    'Esse link tem a validade de 24h a partir de agora.',
                                form=get_user_email_form)

    else:
        return render_template('accounts/getuseremail.html',
                               form=get_user_email_form)

@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username = request.form['username']
        email = request.form['email']

        # Check usename exists
        user = Users.query.filter_by(username=username).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Nome do usuário já cadastrado',
                                   success=False,
                                   form=create_account_form)

        # Check email exists
        user = Users.query.filter_by(email=email).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Email já cadastrado',
                                   success=False,
                                   form=create_account_form)

        # else we can create the user
        user = Users(**request.form)
        db.session.add(user)
        db.session.commit()

        return render_template('accounts/register.html',
                               msg='Usuário cadastrado, por favor faça o <a href="/login">login!</a>',
                               success=True,
                               form=create_account_form)

    else:
        return render_template('accounts/register.html', form=create_account_form)


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

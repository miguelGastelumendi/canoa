# -*- encoding: utf-8 -*-us
"""
Copyright (c) 2019 - present AppSeed.us
"""
import datetime
import requests
import os

from flask import render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_user,
    logout_user
)
from sqlalchemy import or_
from apps import db, login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, CreateAccountForm, ChangePasswordForm, GetUserEmailForm
from apps.authentication.models import users
from apps.authentication.util import verify_pass, hash_pass
from apps.home.emailstuff import sendEmail
from apps.home.dbquery import executeSQL, getValues
import secrets
from apps.home.helper import getTexts, getErrorMessage
from apps.home.logHelper import Log2Database

log = Log2Database()

@blueprint.route('/')
def route_default():
    return redirect(url_for('authentication_blueprint.login'))

# Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    #log.logActivity2Database(idUsuario='NULL',
    #                         idProjeto='NULL',
    #                         url=f'/login/{request.form["username"]}/{request.form["password"]}' if 'login' in request.form else '/login')
    login_form = LoginForm(request.form)
    texts = getTexts('login')
    if 'login' in request.form:

        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        #user = users.query.filter_by(username=username).first()
        user = users.query.filter(or_(users.username==username, users.email==username)).first()
        # Check the password
        if user and verify_pass(password, user.password):

            login_user(user)
            return redirect(url_for('authentication_blueprint.route_default'))

        # Something (user or pass) is not ok
        texts['msgError'] = getErrorMessage('userOrPwdIsWrong')
        return render_template('accounts/login.html',
                               form=login_form,
                               **texts)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form,
                               **texts
                               )

    return redirect(url_for('home_blueprint.index'))

# { to_str ================================================
# mgd 2024.03.21
#----------------------------------------------------------
def to_str(s: str):
    return '' if s is None else s.strip()
# to_str } ================================================

# { Logger ================================================
# mgd 2024.03.21
def logger(url: str):
   idProjectKey= '_projeto_id'
   idProject= db.session[idProjectKey] if  current_user.is_authenticated and idProjectKey in db.session.keys() else -1
   idUser= current_user.id if current_user.is_authenticated else -1

   # assis log.logActivity2Database(idUser, idProject, url)
# Logger } ================================================

# { isMethodGet ===========================================
# mgd 2024.03.21
def isMethodGet():
   isGet= True
   if request.method == 'POST':
       isGet= False
   elif not isGet:
       raise ValueError('Unexpected request method')

   return isGet
# isMethodGet } ===========================================

# { changepassword ========================================
# Change Password for `authenticated user` or with Token
# mgd 2024.03.21
@blueprint.route('/changepassword', methods= ['POST', 'GET'])
@blueprint.route('/changepassword/<token>', methods=['GET','POST'])
def changepassword(token= None):
   route= 'changepassword'
   template = f'accounts/{route}.html'
   isGet= isMethodGet()
   hasToken= token != None
   sToken= to_str(token)
   tokenIsValid = True # TODO: hasToken if ValidateToken(token) else True
   logger(f'@{request.method.lower()}:/{route}/{sToken}')

   changepassword_form= ChangePasswordForm(request.form)
   texts= getTexts(route)

   if not tokenIsValid:
      texts['msgError']= getErrorMessage('invalidRequest')

   elif (current_user.is_authenticated and hasToken):
      texts['msgError']= getErrorMessage('invalidRequest')

   elif not (current_user.is_authenticated or hasToken):
      texts['msgError']= getErrorMessage('invalidRequest')

   elif not isGet:
      password= to_str(request.form['password'])
      confirm_password= to_str(request.form['confirm_password'])

      if (len(password) < 6):
         texts['msgError']= getErrorMessage('invalidPassword')

      elif password != confirm_password:
         texts['msgError']= getErrorMessage('passwordsAreDifferent')

      elif not current_user.is_authenticated:
         user = users.query.filter_by(recoveremailtoken=token).first()
         user.password = hash_pass(password)
         db.session.add(user)
         db.session.commit()
         #TODO give msg and goto
         texts['urlGoto'] = url_for('authentication_blueprint.login');
         return redirect(url_for('authentication_blueprint.login'))

      #else #user is_authenticated

   return render_template(
       template,
       form= changepassword_form,
       **texts
      )

# changepassword } ========================================


# { changepassword ======================================
# User with Token Change Password Routine

# @blueprint.route('/changepassword/<token>', methods=['GET','POST'])
# def changepassword(token=None):
#    route= 'changepassword'
#    isGet= isMethodGet()
#    logger(f'@{request.method.lower()}:/{route}')

#    texts= getTexts('route')
#    changepassword_form= ChangePasswordForm(request.form)


#    if 'password' in request.form:
#       #read form data
#       password = request.form['password']
#       confirm_password = request.form['confirm_password']
#       if password == confirm_password:
#             user = users.query.filter_by(recoveremailtoken=token).first()
#             user.password = hash_pass(password)
#             db.session.add(user)
#             db.session.commit()
#             return redirect(url_for('authentication_blueprint.login'))
#       else:
#           texts['msgError'] = getErrorMessage('passwordsAreDifferent')
#           return render_template('accounts/changepassword.html',
#                                  form=changepassword_form,
#                                  **texts)
#    else:
#       recoverEmailTimeStamp = getValues("select recoverEmailTimeStamp from users "
#                                        f"where recoverEMailToken = '{token}'")
#       if recoverEmailTimeStamp == None:
#          texts['msgError'] = getErrorMessage('linkExpired')

#       elif (datetime.datetime.now() - recoverEmailTimeStamp).days > 1:
#          get_user_email_form = GetUserEmailForm(request.form)
#          texts['msgError'] = getErrorMessage('passwordsAreDifferent')
#          return render_template('accounts/getuseremail.html',
#                                  form=get_user_email_form,
#                                  **texts)
#    return render_template('accounts/changepassword.html',
#                         form=changepassword_form,
#                         **texts)


@blueprint.route('/getuseremail', methods=['GET', 'POST'])
def getuseremail():

    #log.logActivity2Database(idUsuario=current_user.id if current_user else -1,
    #idProjeto=-1 if not '_projeto_id' in session.keys() else session['_projeto_id'],
    #                         url=f'/get_user_email')
    texts = getTexts('getuseremail')
    get_user_email_form = GetUserEmailForm(request.form)
    if 'user_email' in request.form:
        toEMail = request.form['user_email']

        if getValues(f"select count(1) from users where email = '{toEMail}'") != 1:
            texts['msgError'] = getErrorMessage('emailNotRegistered')
            return render_template('accounts/getuseremail.html',
                                   form=get_user_email_form,
                                   **texts)
        token = secrets.token_urlsafe()
        ip = requests.get('https://checkip.amazonaws.com').text.strip()
        url = f"{os.environ['CAATINGA_CHANGE_PWD_EMAIL_LINK']}{url_for('authentication_blueprint.changepassword', token=token)}"
        #url = f"http://{ip}:50051{url_for('authentication_blueprint.changepassword',token=token)}"
        sendEmail(toEMail, 'emailChangePassword', {'url': url})
        executeSQL(f"update users set recoverEmailToken = '{token}',"
                   f" recoverEmailTimeStamp = current_timestamp "
                   f"where email = '{toEMail}'")
        texts['msgError'] = getErrorMessage('emailSent')
        return render_template('accounts/getuseremail.html',
                               form=get_user_email_form,
                               **texts)
    else:
        return render_template('accounts/getuseremail.html',
                               form=get_user_email_form,
                               **texts)

@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    #log.logActivity2Database(idUsuario=current_user.id if current_user else -1,
    #idProjeto=-1 if not '_projeto_id' in session.keys() else session['_projeto_id'],
    #                         url=f'/register/{request.form["username"] if "register" in request.form else ""}/{request.form["email"] if "register" in request.form else ""}'
    #                         )
    texts = getTexts('register')
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username = request.form['username']
        email = request.form['email']

        # Check usename exists
        user = users.query.filter_by(username=username).first()
        if user:
            texts['msgError'] = getErrorMessage('userAlreadyRegistered')
            return render_template('accounts/register.html',
                                   success=False,
                                   form=create_account_form,
                                   **texts)

        # Check email exists
        user = users.query.filter_by(email=email).first()
        if user:
            texts['msgError'] = getErrorMessage('emailAlreadyRegistered')
            return render_template('accounts/register.html',
                                   success=False,
                                   form=create_account_form,
                                   **texts)

        # else we can create the user
        user = users(**request.form)
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
    #log.logActivity2Database(idUsuario=current_user.id if current_user else -1,
    #                         idProjeto=-1 if not '_projeto_id' in session.keys() else session['_projeto_id'],
    #                         url=f'/logout/{request.form["username"] if "register" in request.form else ""}'
    #                         )
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

#eof
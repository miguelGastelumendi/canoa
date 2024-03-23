# -*- encoding: utf-8 -*-us
"""
 The Caatinga Team 2024
 ----------------------
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
from apps.authentication.forms import LoginForm, RegisterForm, ChangePasswordForm, RequestEmailForm
from apps.authentication.models import users
from apps.authentication.util import verify_pass, hash_pass
from apps.home.emailstuff import sendEmail
from apps.home.dbquery import executeSQL, getValues
import secrets
from apps.home.helper import getTexts, add_msg_success, add_msg_error
from apps.home.logHelper import Log2Database

log= Log2Database()

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
   logged= False if not current_user else current_user.is_authenticated
   idProject= db.session[idProjectKey] if logged and hasattr(db.session, 'keys') and idProjectKey in db.session.keys(idProjectKey) else -1
   idUser= current_user.id if current_user.is_authenticated else -1

   # assis log.logActivity2Database(idUser, idProject, url)
# Logger } ------------------------------------------------

# { is_method_get =========================================
# mgd 2024.03.21
def is_method_get():
   is_get= True
   if request.method == 'POST':
       is_get= False
   elif not is_get:
       # if not is_get then is_post, there is no other possibility
       raise ValueError('Unexpected request method.')

   return is_get
# is_method_get } -----------------------------------------

# { token_exists =========================================-
# mgd 2024.03.22
def token_exists(token: str) -> bool:
   return (len(token) > 10) and getValues(f"select recoverEmailTimeStamp from users where recoveremailtoken = '{token}'")
# token_exists } -----------------------------------------

# { is_token_valid ========================================
# mgd 2024.03.22
def is_token_valid(token: str, days: int) -> bool:
   token = to_str(token)
   time_stamp = getValues("select recoverEmailTimeStamp from users where recoveremailtoken = '{token}'")
   if (time_stamp == None):
      days = -1
   else:
      days= (datetime.datetime.now() - time_stamp).days

   return 0 <= days <= 1
# is_token_valid } ----------------------------------------


@blueprint.route('/')
def route_default():
    if current_user.is_authenticated:
      return redirect(url_for('home_blueprint.index'))
    else:
      return redirect(url_for('authentication_blueprint.login'))


# { login =================================================
@blueprint.route('/login', methods= ['GET', 'POST'])
def login():
   route= 'login'
   template= f'accounts/{route}.html'
   is_post= not is_method_get()
   logger(f'@{request.method.lower()}:/{route}')

   # deixar rodar login
   # if current_user.is_authenticated:
   #    return redirect(url_for('home_blueprint.index'))

   tmpl_form= LoginForm(request.form)
   texts= getTexts(route)

   if is_post:
      username= to_str(request.form['username'])
      password= to_str(request.form['password'])

      user= users.query.filter(or_(users.username==username, users.email==username)).first()
      if user and verify_pass(password, user.password):
         login_user(user)
         return redirect(url_for('home_blueprint.index'))

      # Something (user or pass) is not ok, retutn
      add_msg_error('userOrPwdIsWrong', texts)

   return render_template(
       template,
       form= tmpl_form,
       **texts
      )
# login } -------------------------------------------------

# { changepassword ========================================
# Change Password for `authenticated user` or with a token
# mgd 2024.03.21
@blueprint.route('/changepassword', methods= ['POST', 'GET'])
@blueprint.route('/changepassword/<token>', methods= ['GET','POST'])
def changepassword(token= None):
   success_btn = 'chgPwSuccessBtn'
   success_link = 'chgPwSuccessLink'
   route= 'changepassword'
   template= f'accounts/{route}.html'
   is_get= is_method_get()
   token_send= token != None
   token_str= to_str(token)
   days= 0
   success= False
   password= '' if is_get else to_str(request.form['password'])
   confirm_password= '' if is_get else to_str(request.form['confirm_password'])
   logger(f'@{request.method.lower()}:/{route}/{token_str}')


   tmpl_form= ChangePasswordForm(request.form)
   texts= getTexts(route)

   if not (token_send and token_exists(token_str)):
      add_msg_error('invalidToken', texts)

   elif (token_send and current_user.is_authenticated):
      add_msg_error('invalidRequest', texts)

   elif not (token_send or current_user.is_authenticated):
      add_msg_error('invalidRequest', texts)

   elif is_get:
      pass

   elif (len(password) < 6): # TODO: tmpl_form.password.validators[1].min
      add_msg_error('invalidPassword', texts)

   elif password != confirm_password:
      add_msg_error('passwordsAreDifferent', texts)

   elif current_user.is_authenticated:
      user.password= hash_pass(password)
      db.session.add(user)
      db.session.commit()
      add_msg_success('chgPwUserSuccess', texts)
      texts[success_btn] = add_msg_success('chgPwSuccessUserBtn')
      texts[success_link] = url_for('home_blueprint.index')
      success= True

   elif not is_token_valid(days):
      add_msg_error('invalidToken' if days < 0 else 'expiredToken', texts)

   else: # user has a valid token
      user= users.query.filter_by(recoveremailtoken=token).first()
      user.password= hash_pass(password)
      db.session.add(user)
      db.session.commit()
      add_msg_success('chgPwTokenSuccess', texts)
      texts[success_btn] = add_msg_success('chgPwSuccessTokenBtn' )
      texts[success_link] = url_for('authentication_blueprint.login')
      success= True

   return render_template(
       template,
       form= tmpl_form,
       success= success,
       **texts
      )
# changepassword } ----------------------------------------


# { requestemail ==========================================
@blueprint.route('/requestemail', methods= ['GET', 'POST'])
def requestemail():
   route= 'requestemail'
   template= f'accounts/{route}.html'
   is_get=  is_method_get()
   logger(f'@{request.method.lower()}:/{route}')
   success = False

   texts= getTexts(route)
   tmpl_form= RequestEmailForm(request.form)
   send_to=  '' if is_get else to_str(request.form['user_email'])

   if is_get:
      pass

   elif getValues(f"select count(1) from users where email = '{send_to}'") != 1:
      add_msg_error('emailNotRegistered', texts)

   else:
      token= secrets.token_urlsafe()
      ip= requests.get('https://checkip.amazonaws.com').text.strip()
      url= f"{os.environ['CAATINGA_CHANGE_PWD_EMAIL_LINK']}{url_for('authentication_blueprint.changepassword', token=token)}"
      #url= f"http://{ip}:50051{url_for('authentication_blueprint.changepassword',token=token)}"
      #TODO: try/catch
      # TESTE sendEmail(send_to, 'emailChangePassword', {'url': url})
      executeSQL(f"update users set recoveremailtoken= '{token}',"
                 f" recoveremailtimestamp= current_timestamp"
                 f" where email = '{send_to}'")

      add_msg_success('emailSent', texts)
      success = True


   return render_template(template,
                          success= success,
                           form= tmpl_form,
                           **texts)

# requestemail } ------------------------------------------

# { register ==============================================
@blueprint.route('/register', methods= ['GET', 'POST'])
def register():
   route= 'register'
   template= f'accounts/{route}.html'
   is_get= is_method_get()
   logger(f'@{request.method.lower()}:/{route}')

   texts= getTexts('register')
   tmpl_form= RegisterForm(request.form)

   if is_get:
      return render_template(template,
                             success=False,
                             form=tmpl_form,
                             **texts)

   # Teste de success
   # add_msg_success('welcome', texts)
   # return render_template('accounts/register.html',
   #                         success=True,
   #                         form=tmpl_form,
   #                         **texts)


   # is_post:
   username= request.form['username']
   email= request.form['email']

   user= users.query.filter_by(username=username).first()
   if user:  #user exists!
      add_msg_error('userAlreadyRegistered', texts);
      return render_template(template,
                              success=False,
                              form=tmpl_form,
                              **texts)

   user= users.query.filter_by(email=email).first()
   if user: #email exists!
         add_msg_error('emailAlreadyRegistered', texts)
         return render_template(template,
                              success=False,
                              form=tmpl_form,
                              **texts)

   # else we can create the user ;-)
   user= users(**request.form)
   db.session.add(user)
   db.session.commit()
   add_msg_success('welcome', texts)

   return render_template('accounts/register.html',
                           success=True,
                           form=tmpl_form,
                           **texts)
# register } ----------------------------------------------

# { logout ================================================
@blueprint.route('/logout')
def logout():
   logger(f'@{request.method.lower()}:/logout')
   logout_user()
   return redirect(url_for('authentication_blueprint.login'))
# logout } ------------------------------------------------

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
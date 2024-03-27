# -*- encoding: utf-8 -*-us
"""
 The Caatinga Team 2024
 ----------------------
 """
# cSpell:ignore passwordrecovery recoveremailtoken recoveremailtimestamp lastpasswordchange

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
from flask_login import login_required
from apps.authentication.forms import LoginForm, RegisterForm, NewPasswordForm, PasswordRecoveryForm
from apps.authentication.models import users
from apps.authentication.util import verify_pass, hash_pass
from apps.home.emailstuff import sendEmail
from apps.home.dbquery import executeSQL, getValues
import secrets
from apps.home.texts import get_texts, add_msg_success, add_msg_error
from apps.home.logHelper import Log2Database
from collections import namedtuple

log= Log2Database()

# { to_str ================================================
def to_str(s: str):
    return '' if s is None else s.strip()
# to_str } ------------------------------------------------

# { get_user_row ==========================================
def get_user_row():
   user_row = None
   if current_user and current_user.is_authenticated:
      user_row= users.query.filter_by(id = current_user.id).first()

   return user_row
# get_user_row } ------------------------------------------


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

# { tokenValid ============================================
#  True when the number of days since issuance is less than
#  or equal to `max`
def tokenValid(time_stamp, max: int) -> bool:
   days= (datetime.datetime.now() - time_stamp).days
   return 0 <= days <= max
# tokenValid } --------------------------------------------

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


   # TODO: Ask for logout
   if current_user.is_authenticated and not is_post:
      return unauthorized_handler()


   tmpl_form= LoginForm(request.form)
   texts= get_texts(route)

   if is_post:
      username= to_str(request.form['username'])
      password= to_str(request.form['password'])
      search_for= to_str(username).lower()

      user= users.query.filter(or_(users.search_name == search_for, users.email == search_for)).first()
      if user and verify_pass(password, user.password):
         remember_me = to_str(request.form.get('remember_me')); # not always returns
         login_user(user, remember_me)
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
# Change Password of the `authenticated user`
# mgd 2024.03.21
@blueprint.route('/changepassword', methods= ['GET','POST'])
@login_required
def changepassword():
   route= 'changepassword'
   template= f'accounts/rst_chg_password.html'
   is_get= is_method_get()
   success= False
   password= '' if is_get else to_str(request.form['password'])
   confirm_password= '' if is_get else to_str(request.form['confirm_password'])
   user= None if is_get else get_user_row()
   logger(f'@{request.method.lower()}:/{route}/')


   tmpl_form= NewPasswordForm(request.form)
   texts= get_texts(route)
   #TODO if current_user.is_authenticated redirect to logoff

   if is_get:
      pass

   elif (len(password) < 6): # TODO: tmpl_form.password.validators[1].min
      add_msg_error('invalidPassword', texts)

   elif password != confirm_password:
      add_msg_error('passwordsAreDifferent', texts)

   elif user == None:
      logout()

   else:
      user.password= hash_pass(password)
      db.session.add(user)
      db.session.commit()
      add_msg_success('chgPwSuccess', texts)
      success= True

   return render_template(
       template,
       form= tmpl_form,
       success= success,
       **texts
      )
# changepassword } ----------------------------------------

# { resetpassword ==========================================
# mgd 2024.03.21
""""
   Password Reset Form:
   When a user forgets their password, they will receive an
   email containing a link to a form where they can enter
   and confirm their new password.
"""
@blueprint.route('/resetpassword/<token>', methods= ['GET','POST'])
def resetpassword(token= None):
   route= 'resetpassword'
   template= f'accounts/rst_chg_password.html'
   is_get= is_method_get()
   success= False
   token_str= to_str(token)
   logger(f'@{request.method.lower()}:/{route}/{token_str}')
   password= '' if is_get else to_str(request.form['password'])
   confirm_password= '' if is_get else to_str(request.form['confirm_password'])

   tmpl_form= NewPasswordForm(request.form)
   texts= get_texts(route)

   if current_user.is_authenticated:
      logout()
      return unauthorized_handler()

   elif len(token_str) < 12:
      add_msg_error('invalidToken', texts)

   elif is_get:
      pass

   elif (len(password) < 6): # TODO: tmpl_form.password.validators[1].min
      add_msg_error('invalidPassword', texts)

   elif password != confirm_password:
      add_msg_error('passwordsAreDifferent', texts)

   else:
      user= users.query.filter_by(recoveremailtoken=token_str).first()
      if user == None:
         add_msg_error('invalidToken', texts)

      elif not tokenValid(user.recoveremailtimestamp, 5):
         add_msg_error('expiredToken', texts)

      else:
         user.password= hash_pass(password)
         user.recoveremailtoken= None
         #user.lastpasswordchange= datetime.datetime.now()
         db.session.add(user)
         db.session.commit()
         add_msg_success('resetPwSuccess', texts)
         success= True

   return render_template(
       template,
       form= tmpl_form,
       success= success,
       **texts
      )
# resetpassword } ----------------------------------------


# { passwordrecovery ======================================
""""
   Password Recovery Form
   This form asks for the registered email so that a link
   with a token can be sent to it.
   *user is should not be authenticated*
"""
@blueprint.route('/passwordrecovery', methods= ['GET', 'POST'])
def passwordrecovery():

   if current_user.is_authenticated:
      # como que oc chegou aqui, vai para
      return redirect(url_for('home_blueprint.changepassword'))

   route= 'passwordrecovery'
   template= f'accounts/{route}.html'
   is_get=  is_method_get()
   logger(f'@{request.method.lower()}:/{route}')
   success = False

   texts= get_texts(route)
   tmpl_form= PasswordRecoveryForm(request.form)
   send_to= '' if is_get else to_str(request.form['user_email'])

   if is_get:
      pass

   # TODO: get  user= users.query.filter_by(email=send_to).first() => use instead of update
   elif getValues(f"select count(1) from users where email = '{send_to}'") != 1:
      add_msg_error('emailNotRegistered', texts)

   else:
      token= secrets.token_urlsafe()
      ip= requests.get('https://checkip.amazonaws.com').text.strip()
      #url= f"{os.environ['CAATINGA_CHANGE_PWD_EMAIL_LINK']}{url_for('authentication_blueprint.changepassword', token=token)}"
      url= f"http://{ip}:50051{url_for('authentication_blueprint.changepassword',token=token)}"

      sendEmail(send_to, 'emailPasswordRecovery', {'url': url})
      update = (f"update users set recoveremailtoken= '{token}',"
                f" recoveremailtimestamp= current_timestamp"
                f" where email = '{send_to}'")
      executeSQL(update)

      add_msg_success('emailSent', texts)
      success = True

   return render_template(template,
                          success= success,
                          form= tmpl_form,
                          **texts)
# passwordrecovery } --------------------------------------

# { register ==============================================
@blueprint.route('/register', methods= ['GET', 'POST'])
def register():
   route= 'register'
   template= f'accounts/{route}.html'
   is_get= is_method_get()
   logger(f'@{request.method.lower()}:/{route}')

   texts= get_texts('register')
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
   username= to_str(request.form['username'])
   email= to_str(request.form['email'])
   search_for= username.lower()

   user= users.query.filter_by(search_name = search_for).first()
   if user:  # user exists!
      add_msg_error('userAlreadyRegistered', texts);
      return render_template(template,
                              success=False,
                              form=tmpl_form,
                              **texts)

   user= users.query.filter_by(email = email.lower()).first()
   if user: # e-mail exists!
         add_msg_error('emailAlreadyRegistered', texts)
         return render_template(template,
                              success=False,
                              form=tmpl_form,
                              **texts)

   if user.disable: # ups!
         add_msg_error('userIsDisabled', texts)
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

# Errors --------------------------------------------------

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
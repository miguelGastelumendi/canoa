# -*- encoding: utf-8 -*-us
"""
 Equipe da Canoa -- 2024

 mgd
 ----------------------
 """
# cSpell:ignore passwordrecovery recover_email_token  lastpasswordchange tmpl errorhandler assis, uploadfile, sqlalchemy, werkzeug

import requests
import secrets
import os

from filecmp import cmp as file_cmp
from flask import render_template, redirect, request, url_for
from sqlalchemy import or_
from flask_login import current_user, login_user, logout_user
from flask_login import login_required
from carranca import db, login_manager
from authentication import blueprint
from werkzeug.utils import secure_filename

from .forms import LoginForm, RegisterForm, NewPasswordForm, PasswordRecoveryForm, UploadFileForm
from .models import Users, UserDataFiles
from .util import verify_pass, hash_pass, is_user_logged
from .data_validate import submit_to_data_validate
from .validate import do_uploaded_files_folder, data_validate, save_file_and_record, validate_file

from ..scripts.logHelper import Log2Database
from ..scripts.textsHelper import add_msg_error, get_section
from ..scripts.pyHelper import now, is_str_none_or_empty
from ..scripts.carranca_config import CarrancaConfig


log= Log2Database()


# { Logger ================================================
# mgd 2024.03.21
def logger( sMsg, type = 'info', *args):
   logged= is_user_logged()
   idUser= current_user.id if logged else -1
   log_str= (sMsg + '').format(args) if args else sMsg
   print( log_str )
   # assis log.logActivity2Database(idUser, idProject, url)
# Logger } ------------------------------------------------


# ---------------------------------------------------------
#  Routes Helpers
# ---------------------------------------------------------

# { to_str ================================================
def _to_str(s: str):
    return '' if s is None else s.strip()
# to_str } ------------------------------------------------

# { _index_url ============================================
def _index_url():
    return url_for('home_blueprint.index')
# _index_url } --------------------------------------------


# { get_user_row ==========================================
def _get_user_row():
   user_row = None
   if is_user_logged():
      user_row= Users.query.filter_by(id = current_user.id).first()

   return user_row
# get_user_row } ------------------------------------------

# { is_method_get =========================================
# mgd 2024.03.21
def _is_method_get():
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
    days= (now() - time_stamp).days
    return 0 <= days <= max
# tokenValid } --------------------------------------------

# { internal_logout  ======================================
def internal_logout():
    logout_user()
# internal_logout } =======================================

# { _get_input_text  ======================================
def _get_input_text(name: str) -> str:
    text = request.form.get(name)
    return _to_str(text)
# _get_input_text } =======================================

# { _prepare_route_entry ==================================
def _prepare_route_entry(route: str) -> str:
    template = f'accounts/{route}.html.j2'
    is_get= _is_method_get()
    logged = is_user_logged()

    index_url = None if logged else _index_url()
    redirect = '' if logged else " [User is not logged,  will be redirect to index]"
    logger(f'@{request.method.lower()}:/{route}{redirect}')
    texts = get_section(route) if logged else None

    return template, is_get, index_url, texts
# _prepare_route_entry } ----------------------------------


# ---------------------------------------------------------
#   Account Routes
# ---------------------------------------------------------

# { default route =========================================
@blueprint.route('/')
def route_default():
    if is_user_logged():
      return redirect(_index_url())
    else:
      return redirect(url_for('authentication_blueprint.login'))

# default route } =========================================

# { upload file ============================================
# see https://flask.palletsprojects.com/en/3.0.x/patterns/fileuploads/
@login_required
@blueprint.route('/uploadfile', methods= ['GET', 'POST'])
def uploadfile():

    template, is_get, index_url, texts = _prepare_route_entry('uploadfile')
    if index_url:
       return redirect(index_url)

    tmpl_form = UploadFileForm(request.form)
    file_obj = None if (is_get or not request.files) else request.files[tmpl_form.filename.id]
    file_name_secure = None if file_obj == None else secure_filename(file_obj.filename)
    user_code = CarrancaConfig.user_code(current_user.id)
    uploaded_files_folder = os.path.join(CarrancaConfig.folder_uploaded_files, user_code)

    # error helpers
    _file = ""
    user_error = 'uploadFileError' #
    except_error = ""
    removed = ""
    ve = texts["validExtensions"]
    valid_extensions = ".zip" if is_str_none_or_empty(ve) else ve.lower()
    task_code = 0

    # start the check!
    if is_get:
        task_code = 0
    elif not request.files:
        task_code+= 1
    elif file_obj is None:
        task_code+= 2
    elif is_str_none_or_empty(current_user.email):
        task_code+= 3
    elif is_str_none_or_empty(file_name_secure):
        task_code+= 4
    elif not file_cmp(file_obj.filename, file_name_secure): #invalid name, be careful
        task_code+= 5
    elif len(file_name_secure) > 130: # UserDataFiles.file_name.length
        task_code+= 6
    elif not any(file_name_secure.lower().endswith(ext.strip()) for ext in valid_extensions.split(',')):
        task_code+= 7
    #elif not response.headers.get('Content-Type') == ct in valid_content_types.split(',')): #check if really zip
        #task_code+= 8
    elif not do_uploaded_files_folder(uploaded_files_folder):
        task_code+= 9
    else:
        task_code = data_validate(current_user, user_code, file_obj, uploaded_files_folder, file_name_secure)



    if (err_code != 0):
        show_error = add_msg_error(user_error, texts, err_code)
        logger( f"{show_error} | File stage '{_file}' |{removed} Code {err_code} | Exception Error '{except_error}'." )


    return render_template(
        template,
        form= tmpl_form,
        **texts
    )


# { login =================================================
@blueprint.route('/login', methods= ['GET', 'POST'])
def login():
   route= 'login'
   template= f'accounts/{route}.html.j2'
   is_post= not _is_method_get()
   logger(f'@{request.method.lower()}:/{route}')


   # TODO: Ask for logout
   if is_user_logged() and not is_post:
      return redirect(url_for('home_blueprint.index'))

   tmpl_form= LoginForm(request.form)
   texts= get_section(route)

   if is_post:
      username= _get_input_text('username')
      password= _get_input_text('password')
      search_for= _to_str(username).lower()

      user= Users.query.filter(or_(Users.username_lower == search_for, Users.email == search_for)).first()
      if not user or not verify_pass(password, user.password):
         add_msg_error('userOrPwdIsWrong', texts)

      elif user.disabled:
         add_msg_error('userIsDisabled', texts)

      else:
         remember_me = _to_str(request.form.get('remember_me')); # not always returns
         login_user(user, remember_me)
         # test: confirm_login()
         return redirect(url_for('home_blueprint.index'))

   return render_template(
       template,
       form= tmpl_form,
       **texts
      )
# login } -------------------------------------------------

# { changepassword ========================================
# Change Password of the `authenticated user`
# mgd 2024.03.21
# todo login_required()
# todo: 2024.04.01 fresh_login_required()
@blueprint.route('/changepassword', methods= ['GET','POST'])
def changepassword():

   # TODO: Ask for logout
   if not is_user_logged():
      # TODO: form que fala: solicitação invalida, você será redirecionado a:
      return redirect(url_for('authentication_blueprint.login'))

   route= 'changepassword'
   template= f'accounts/rst_chg_password.html.j2'
   is_get= _is_method_get()
   success= False
   password= '' if is_get else _get_input_text('password')
   confirm_password= '' if is_get else _get_input_text('confirm_password')
   user= None if is_get else _get_user_row()
   logger(f'@{request.method.lower()}:/{route}/')

   tmpl_form= NewPasswordForm(request.form)
   texts= get_section(route)

   if is_get:
      pass

   elif (len(password) < 6): # TODO: tmpl_form.password.validators[1].min
      add_msg_error('invalidPassword', texts)

   elif password != confirm_password:
      add_msg_error('passwordsAreDifferent', texts)

   elif user == None:
      internal_logout()
      redirect(url_for('authentication_blueprint.login'))

   else:
      user.password= hash_pass(password)
      db.session.add(user)
      db.session.commit()
      add_msg_success('chgPwSuccess', texts)
      internal_logout()
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
   template= f'accounts/rst_chg_password.html.j2'
   is_get= _is_method_get()
   success= False
   token_str= _to_str(token)
   logger(f'@{request.method.lower()}:/{route}/{token_str}')
   password= '' if is_get else _get_input_text('password')
   confirm_password= '' if is_get else _get_input_text('confirm_password')

   tmpl_form= NewPasswordForm(request.form)
   texts= get_section(route)

   if is_user_logged():
      internal_logout()
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
      user= Users.query.filter_by(recover_email_token = token_str).first()
      if user == None:
         add_msg_error('invalidToken', texts)

      elif not tokenValid(user.recover_email_token_at, 5):
         add_msg_error('expiredToken', texts)

      else:
         user.password= hash_pass(password)
         user.recover_email_token= None
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

   if is_user_logged():
      # como é que oc chegou aqui, vai para
      return redirect(url_for('authentication_blueprint.changepassword'))

   route= 'passwordrecovery'
   template= f'accounts/{route}.html.j2'
   is_get=  _is_method_get()
   logger(f'@{request.method.lower()}:/{route}')
   success = False

   texts= get_section(route)
   tmpl_form= PasswordRecoveryForm(request.form)
   send_to= '' if is_get else _get_input_text('user_email').lower()
   user= None if is_get else Users.query.filter_by(email = send_to).first()

   if is_get:
      pass

   elif user == None:
      add_msg_error('emailNotRegistered', texts)

   else:
      code = 7 #TODO, error code
      try:
         token= secrets.token_urlsafe()
         ip= requests.get('https://checkip.amazonaws.com').text.strip()
         url= f"http://{ip}:50051{url_for('authentication_blueprint.resetpassword', token=token)}"

         send_email(send_to, 'emailPasswordRecovery', {'url': url})
         user.recover_email_token= token   # recover_email_token_at updated in trigger
         db.session.add(user)
         db.session.commit()
         add_msg_success('emailSent', texts)

         success = True
      except: #TODO: log
         add_msg_error('emailNotSent', texts)

   return render_template(template,
                          success= success,
                          form= tmpl_form,
                          **texts)
# passwordrecovery } --------------------------------------

# { register ==============================================
@blueprint.route('/register', methods= ['GET', 'POST'])
def register():
   route= 'register'
   template= f'accounts/{route}.html.j2'
   is_get= _is_method_get()
   logger(f'@{request.method.lower()}:/{route}')

   texts= get_section('register')
   tmpl_form= RegisterForm(request.form)

   if is_get:
      return render_template(template,
                             success=False,
                             form=tmpl_form,
                             **texts)

   #else is_post:
   username= _get_input_text('username')
   email= _get_input_text('email')

   user= Users.query.filter_by(username_lower = username.lower()).first()
   if user:  # user exists!
      add_msg_error('userAlreadyRegistered', texts);
      return render_template(template,
                            success=False,
                            form=tmpl_form,
                            **texts)

   user= Users.query.filter_by(email = email.lower()).first()
   if user: # e-mail exists!
         add_msg_error('emailAlreadyRegistered', texts)
         return render_template(template,
                                success=False,
                                form=tmpl_form,
                                **texts)

   # else we can create the user not disabled ;-)

   user= Users(**request.form)
   user.disabled = False
   db.session.add(user)
   db.session.commit()
   add_msg_success('welcome', texts)

   return render_template(template,
                          success=True,
                          form=tmpl_form,
                          **texts)
# register } ----------------------------------------------

# { logout ================================================
@blueprint.route('/logout')
def logout():
   logger(f'@{request.method.lower()}:/logout')
   internal_logout()
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
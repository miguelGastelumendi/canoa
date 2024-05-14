# -*- encoding: utf-8 -*-us
"""
 Equipe da Canoa -- 2024

 mgd
 ----------------------
 """

# cSpell:ignore assis uploadfile tmpl werkzeug passwordrecovery errorhandler
import requests
import secrets
import os

from flask import render_template, redirect, request, url_for

from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from carranca import db, login_manager
from carranca.authentication import blueprint

from .forms import NewPasswordForm, UploadFileForm
from ..scripts.pwHelper import internal_logout, verify_pass, hash_pass, is_user_logged
from .validate import folder_must_exist, data_validate

from ..scripts.pyHelper import is_same_file_name, is_str_none_or_empty
from ..scripts.logHelper import Log2Database
from ..scripts.routesHelpers import get_input_text, is_method_get
from ..scripts.textsHelper import add_msg_success, add_msg_error, get_section
from ..scripts.email_sender import send_email
from ..scripts.carranca_config import CarrancaConfig

# { Public Vars ===========================================
log= Log2Database()
# ---------------------------------------------------------

# { Logger ================================================
# mgd 2024.03.21
def logger(sMsg, type = 'info', *args) -> str:
   logged= is_user_logged()
   idUser= current_user.id if logged else -1
   log_str= (sMsg + '').format(args) if args else sMsg
   print( log_str )
   return log_str
   # assis log.logActivity2Database(idUser, idProject, url)
# Logger } ------------------------------------------------

# ---------------------------------------------------------
#  Logged Route Helpers
# ---------------------------------------------------------

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

# { _get_logged_route_data=================================
def _get_logged_route_data(route: str) -> str:
    template = f'accounts/{route}.html.j2'
    is_get= is_method_get()
    logged = is_user_logged()

    index_url = None if logged else _index_url()
    redirect = '' if logged else " [User is not logged,  will be redirect to index (401)]"
    logger(f'@{request.method.lower()}:/{route}{redirect}')
    texts = get_section(route) if logged else None

    return template, is_get, index_url, texts

# _get_logged_route_data } --------------------------------


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

    template, is_get, index_url, texts = _get_logged_route_data('uploadfile')
    if index_url: # not logged, 401
       return redirect(index_url)

    tmpl_form = UploadFileForm(request.form)
    file_obj = None if (is_get or not request.files) else request.files[tmpl_form.filename.id]
    file_name_secure = None if file_obj == None else secure_filename(file_obj.filename)
    user_code = CarrancaConfig.user_code(current_user.id)
    uploaded_files_path = os.path.join(CarrancaConfig.path_uploaded_files, user_code)
    user_data_tunnel_path = os.path.join(CarrancaConfig.path_data_tunnel, user_code)

    # error helpers
    _file = ''
    file_ticket = ''
    upload_msg = 'uploadFileError'
    except_error = ''
    removed = ''
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
    elif not is_same_file_name(file_obj.filename, file_name_secure): #invalid name, be careful
        task_code+= 5
    elif len(file_name_secure) > 130: # UserDataFiles.file_name.length
        task_code+= 6
    elif not any(file_name_secure.lower().endswith(ext.strip()) for ext in valid_extensions.split(',')):
        task_code+= 7
    #elif not response.headers.get('Content-Type') == ct in valid_content_types.split(',')): #check if really zip
        #task_code+= 8
    elif not folder_must_exist(uploaded_files_path):
        task_code+= 9
    elif not folder_must_exist(os.path.join(user_data_tunnel_path, CarrancaConfig.folder_validate_output)): # create both: .\<user_code>\<report>
        task_code+= 10
    else:
        task_code+= 20
        task_code, upload_msg, file_ticket = data_validate(task_code, current_user, user_code, file_obj, file_name_secure, uploaded_files_path, user_data_tunnel_path)


    if is_get:
       pass
    elif (task_code == 0):
        log_msg = add_msg_success(upload_msg, texts, file_ticket, current_user.email)
        logger( f"Uploadfile: {log_msg}." )
    else:
        log_msg = add_msg_error(upload_msg, texts, task_code)
        logger( f"Uploadfile: {log_msg} | File stage '{_file}' |{removed} Code {task_code} | Exception Error '{except_error}'." )

    return render_template(
        template,
        form= tmpl_form,
        **texts
    )



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
   is_get= is_method_get()
   success= False
   password= '' if is_get else get_input_text('password')
   confirm_password= '' if is_get else get_input_text('confirm_password')
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
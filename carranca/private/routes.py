# Equipe da Canoa -- 2024
# private\routes.py
#
# To access this routes, user must be logged.
#
# mgd
# cSpell: ignore werkzeug uploadfile tmpl

import os
from flask import Blueprint, render_template, redirect, request, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from .models import Users
from .forms import NewPasswordForm, UploadFileForm
from .validate import folder_must_exist, data_validate

from ..scripts.pw_helper import internal_logout, hash_pass, is_user_logged
from ..scripts.py_helper import is_same_file_name, is_str_none_or_empty
from ..scripts.log_helper import Log2Database
from ..scripts.texts_helper import add_msg_success, add_msg_error, get_section
from ..scripts.routes_helpers import bp_name, base_route_private, get_input_text, get_route_data, login_route, redirect_to
from ..scripts.carranca_config import CarrancaConfig

# === module variables ====================================
log= Log2Database()
bp_private = Blueprint(bp_name(base_route_private), base_route_private, url_prefix= '')


# === local ===============================================

# { Logger ================================================
# mgd 2024.03.21
def logger(sMsg, type = 'info', *args) -> str:
   logged= is_user_logged()
   idUser= current_user.id if logged else -1
   log_str= (sMsg + '').format(args) if args else sMsg
   print( log_str )
   return log_str
# Logger } ------------------------------------------------


def _get_user_row():
   user_row = None
   if is_user_logged():
      user_row= Users.query.filter_by(id = current_user.id).first()
   return user_row


# === routes =============================================

@bp_private.route("/home")
def home():
    route = 'home'
    if not is_user_logged():
        return redirect_to(login_route(), None)

    template = f"{route}/home.html.j2"
    texts = get_section(route)

    return render_template(
        template,
        **texts
    )


@login_required
@bp_private.route('/uploadfile', methods= ['GET', 'POST'])
def uploadfile():
    template, is_get, login_route, texts = get_route_data('uploadfile')
    if login_route: # not logged, send to login
       return redirect_to(login_route)

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
@login_required
@bp_private.route('/changepassword', methods= ['GET','POST'])
def changepassword():
    template, is_get, login_route, texts = get_route_data('changepassword', 'rst_chg_password')
    if login_route: # not logged, 401
        return redirect_to(login_route)

    success = False
    password = '' if is_get else get_input_text('password')
    confirm_password = '' if is_get else get_input_text('confirm_password')
    user = None if is_get else _get_user_row()
    tmpl_form= None if is_get else NewPasswordForm(request.form)

    if is_get:
        pass

    elif (len(password) < 6): # TODO: tmpl_form.password.validators[1].min
        add_msg_error('invalidPassword', texts)
    elif password != confirm_password:
        add_msg_error('passwordsAreDifferent', texts)
    elif user == None:
        internal_logout()
        return redirect_to(login_route)
    else: #TODO try/catch
        user.password= hash_pass(password)
        # db.session.add(user)
        # db.session.commit()
        add_msg_success('chgPwSuccess', texts)
        internal_logout()
        success= True
    return render_template(
            template,
            form= tmpl_form,
            success= success,
            **texts
        )


@bp_private.route('/logout')
def logout():
    internal_logout()
    return redirect_to(login_route())


#eof
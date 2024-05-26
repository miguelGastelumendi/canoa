# Equipe da Canoa -- 2024
# private\routes.py
#
# To access this routes, user must be logged.
#
# mgd
# cSpell: ignore werkzeug uploadfile tmpl

from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

from carranca import db
from carranca.helpers.user_helper import LoggedUser
from .forms import NewPasswordForm, UploadFileForm

from .upload_file.process import process as upload_file_process
from ..public.models import Users
from ..helpers.pw_helper import internal_logout, hash_pass, nobody_logged, someone_logged
from ..helpers.py_helper import is_str_none_or_empty
from ..helpers.log_helper import Log2Database
from ..helpers.user_helper import LoggedUser
from ..helpers.texts_helper import add_msg_success, add_msg_error
from ..helpers.route_helper import bp_name, base_route_private, get_input_text, get_account_form_data, get_private_form_data, login_route, private_route, public_route, redirect_to


# === module variables ====================================
log= Log2Database()
bp_private = Blueprint(bp_name(base_route_private), base_route_private, url_prefix= '')


# === local ===============================================

# { Logger ================================================
# mgd 2024.03.21
def logger(sMsg, type = 'info', *args) -> str:
   logged= someone_logged()
   idUser= current_user.id if logged else -1
   log_str= (sMsg + '').format(args) if args else sMsg
   print( log_str )
   return log_str
# Logger } ------------------------------------------------


# === routes =============================================

@bp_private.route("/home")
def home():
    """
    `home` page is the _landing page_
     for *users* (logged visitors).

    It displays the main menu.
    """

    if not someone_logged():
        return redirect_to(login_route(), None)

    template, _, texts = get_private_form_data('home')

    return render_template(
        template,
        **texts,
        private_route = private_route
    )


@login_required
@bp_private.route('/uploadfile', methods= ['GET', 'POST'])
def uploadfile():
    """
    Throw this route, the user submits a zip file to validate.
    If it passes the simple validations confronted in upload_file.py,
    it is unzipped (see prepare_file.py) and
    sent to the app data_validate (see data_validate.py).
    It's produced report  goes to the via a e-mail and a message is
    displayed to the user.
    Part of Canoa `File Validation` Processes
    """

    if nobody_logged():
       return redirect_to(login_route())

    template, is_get, texts = get_private_form_data('uploadfile')
    tmpl_form = UploadFileForm(request.form)

    if not is_get:
        ve = texts["validExtensions"]
        valid_extensions = (".zip" if is_str_none_or_empty(ve) else ve.lower()).split(',')
        logged_user = LoggedUser(current_user)
        file_obj = request.files[tmpl_form.filename.id] if request.files else None
        error_code, msg_error, msg_exception, data = upload_file_process(logged_user, file_obj, valid_extensions)

        if error_code == 0:
            log_msg = add_msg_success('uploadFileSuccess', texts, data.get('file_ticket'), logged_user.email)
            logger( f"Uploadfile: {log_msg}." )
        else:
            log_msg = add_msg_error(msg_error, texts, error_code)
            #logger( f"Uploadfile: {log_msg} | File stage '{_file}' |{removed} Code {task_code} | Exception Error '{except_error}'." )

    return render_template(
        template,
        form= tmpl_form,
        private_route= private_route,
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
    """
    `changepassword` page, as it's name
    implies, allows the user to change
    is password, for what ever reason
    at all or none.
    Whew! That's four lines :--)
    """

    if nobody_logged():
       return redirect_to(login_route())

    template, is_get, texts = get_account_form_data('changepassword', 'rst_chg_password')
    password = '' if is_get else get_input_text('password')
    confirm_password = '' if is_get else get_input_text('confirm_password')
    user = None if is_get else Users.query.filter_by(id = current_user.id).first() # TODO: Login_Manager
    tmpl_form= NewPasswordForm(request.form)

    if is_get:
        pass
    elif len(password) < 6: # TODO: tmpl_form.password.validators[1].min
        add_msg_error('invalidPassword', texts)
    elif password != confirm_password:
        add_msg_error('passwordsAreDifferent', texts)
    elif user == None:
        internal_logout()
        return redirect_to(login_route())
    else: #TODO try/catch
        user.password= hash_pass(password)
        db.session.add(user)
        db.session.commit()
        add_msg_success('chgPwSuccess', texts)
        internal_logout()

    return render_template(
            template,
            form= tmpl_form,
            public_route = public_route,
            **texts
        )


@bp_private.route('/logout')
def logout():
    internal_logout()
    return redirect_to(login_route())


#eof
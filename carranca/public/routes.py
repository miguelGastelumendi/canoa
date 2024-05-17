# Equipe da Canoa -- 2024
# public\routes.py
#
# This routes are public, users are not required to be logged
#
# mgd
# cSpell: ignore werkzeug uploadfile tmpl sqlalchemy passwordrecovery lastpasswordchange errorhandler assis

import os
import base64
import requests
import secrets
from flask import Blueprint, render_template, url_for, request
from flask_login import login_user
from sqlalchemy import or_

from carranca import db, login_manager
from carranca.private.forms import NewPasswordForm #this form is shared with private

from .forms import LoginForm, RegisterForm, PasswordRecoveryForm
from .html_helper import img_filenames, img_change_src_path

from ..private.models import Users

from ..scripts import log_helper
from ..scripts.pw_helper import internal_logout, is_user_logged, verify_pass, hash_pass
from ..scripts.py_helper import is_str_none_or_empty, to_str, now
from ..scripts.texts_helper import add_msg_error, add_msg_success, get_msg_error, get_text, get_section
from ..scripts.email_sender import send_email
from ..scripts.routes_helpers import bp_name, base_route_public, get_input_text, get_route_data, home_route, index_route, is_method_get, login_route, private_route, public_route, redirect_to

# === module variables ====================================
log = log_helper.Log2Database()  # TODO app
bp_public = Blueprint(bp_name(base_route_public), base_route_public, url_prefix= '')


# === local ===============================================

def _prepare_img_files(html_images: list[str], db_images: list[str], img_path: str, group: str) -> bool:

    img_path_ready = os.path.exists(img_path)
    missing_files = html_images.copy()  # missing files from folder, assume all

    for file_name in html_images:
        if img_path_ready and os.path.exists(os.path.join(img_path, file_name)):
            missing_files.remove(file_name)  # this img is not missing.

    # folder for images & a list of missing_files, are ready.
    # available_files are files that are not on the file system,
    #   but can be retrieved from the DB (db_images says so)
    available_files = [file for file in missing_files if file in db_images]
    if missing_files.count == 0:
        return True  # every file is in file system!

    elif available_files.count == 0:
        return True  # some files missing, but I can't fix it :-(
        # TODO: log this # missing files and no db files to fix

    for file in available_files:
        try:
            b64encoded = get_text(file, group)
            if not is_str_none_or_empty(b64encoded):
                image_data = base64.b64decode(b64encoded)
                with open(os.path.join(img_path, file), "wb") as file:
                    file.write(image_data)
        except Exception as e:
            pass
            # TODO: log

    return True

def _is_token_valid(time_stamp, max: int) -> bool:
    """
    True when the number of days since issuance is less than
    or equal to `max`
    """
    days= (now() - time_stamp).days
    return 0 <= days <= max

# === routes =============================================

@bp_public.route('/')
def route_default():
    if is_user_logged():
      return redirect_to(index_route())
    else:
      return redirect_to(login_route())


@bp_public.route("/index")
def index():
    # @login_required não pode ter, index é 'livre', depende do menu
    # if is_user_logged():
    #     return render_template("home/index.html", pageTitle="Index")
    # else:
    return redirect_to(url_for('authentication_blueprint.login'))

@bp_public.route('/register', methods= ['GET', 'POST'])
def register():
    template, is_get, login_route, texts = get_route_data('register')

    if login_route == None: #user is logged
        return redirect_to(home_route)

    tmpl_form= RegisterForm(request.form)
    if is_get:
        return render_template(template,
                             success=False,
                             form=tmpl_form,
                             href= public_route,
                             **texts
                            )

    #post:
    username= get_input_text('username')
    email= get_input_text('email')

    user= Users.query.filter_by(username_lower = username.lower()).first()
    if user:  # user exists
        add_msg_error('userAlreadyRegistered', texts);
        return render_template(template,
                            success=False,
                            form=tmpl_form,
                            **texts)

    user= Users.query.filter_by(email = email.lower()).first()
    if user: # e-mail exists
        add_msg_error('emailAlreadyRegistered', texts)
        return render_template(template,
                                success=False,
                                form=tmpl_form,
                                **texts)

   # else we can create the user not disabled ;-)
    user= Users(**request.form, disabled = False)  # mgd2: disable como param
    #user.disabled = False
    db.session.add(user)
    db.session.commit()
    add_msg_success('welcome', texts)

    return render_template(template,
                          success=True,
                          form=tmpl_form,
                          **texts)

@bp_public.route('/login', methods= ['GET', 'POST'])
def login():
    template, is_get, login_route, texts = get_route_data('login')
    if login_route is None: # logged, sent to home
       return redirect_to(home_route())

    tmpl_form = LoginForm(request.form)

    if not is_get:
        username= get_input_text('username')
        password= get_input_text('password')
        search_for= to_str(username).lower()

        user= Users.query.filter(or_(Users.username_lower == search_for, Users.email == search_for)).first()
        if not user or not verify_pass(password, user.password):
            add_msg_error('userOrPwdIsWrong', texts)

        elif user.disabled:
            add_msg_error('userIsDisabled', texts)

        else:
            remember_me = to_str(request.form.get('remember_me')); # not always returns
            login_user(user, remember_me)
            # test: confirm_login()
            return redirect_to(home_route())

    return render_template(
            template,
            form= tmpl_form,
            **texts
        )

@bp_public.route('/resetpassword/<token>', methods= ['GET','POST'])
def resetpassword(token= None):
    """
        # mgd 2024.03.21
        Password Reset Form:
        When a user forgets their password, they will receive an
        email containing a link to a form where they can enter
        and confirm their new password.
    """
    if is_user_logged():
        internal_logout()
        return unauthorized_handler()

    template, is_get, _, texts = get_route_data('resetpassword', 'rst_chg_password')
    success = False
    token_str = to_str(token)
    password = '' if is_get else get_input_text('password')
    confirm_password = '' if is_get else get_input_text('confirm_password')

    tmpl_form = NewPasswordForm(request.form)
    if len(token_str) < 12:
        add_msg_error('invalidToken', texts)

    elif is_get:
        pass

    elif (len(password) < 6): # TODO: tmpl_form.password.validators[1].min
        add_msg_error('invalidPassword', texts)

    elif password != confirm_password:
        add_msg_error('passwordsAreDifferent', texts)

    else:
        user = Users.query.filter_by(recover_email_token = token_str).first()
        if user == None:
            add_msg_error('invalidToken', texts)

        elif not _is_token_valid(user.recover_email_token_at, 5):
            add_msg_error('expiredToken', texts)

        else:
            user.password = hash_pass(password)
            user.recover_email_token = None
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


@bp_public.route('/passwordrecovery', methods= ['GET', 'POST'])
def passwordrecovery():
   """"
    Password Recovery Form
    This form asks for the registered email so that a link
    with a token can be sent to it.
    *user should not be authenticated*
   """

   if is_user_logged():
      # como é que oc chegou aqui, vai para
      return redirect_to(private_route('changepassword')) # url_for('authentication_blueprint.changepassword'))

   route= 'passwordrecovery'
   template= f'accounts/{route}.html.j2'
   is_get=  is_method_get()
   #logger(f'@{request.method.lower()}:/{route}')
   success = False

   texts= get_section(route)
   tmpl_form= PasswordRecoveryForm(request.form)
   send_to= '' if is_get else get_input_text('user_email').lower()
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


@bp_public.route("/docs/<docName>")
def docs(docName: str):
    # ============= Documents ============== #
    # TODO:
    #    1. Move path to new CarrancaConfig
    #    1. Only show Public docs if not logged.
    #    2. check if body exists else error
    section = docName
    pageTitle = get_text("pageTitle", section)
    formTitle = get_text("formTitle", section)
    body = get_text("body", section)
    style = get_text("style", section)
    # a comma separated list of images.ext names available on the db,
    # see below db_images & _prepare_img_files
    images = get_text("images", section)

    db_images = (
        [] if is_str_none_or_empty(images) else [s.strip() for s in images.split(",")]
    )  # list of img names in db

    html_images = (
        [] if is_str_none_or_empty(body) else sorted(img_filenames(body))
    )  # list of img tags in HTML

    # TODO: check if this is the best way to get a path
    img_path = os.path.join("\\", "static", "docs", docName, "img")
    if is_str_none_or_empty(body):
        msg = get_msg_error("documentNotFound").format(docName)
        body = f"<h4>{msg}</h4>"
        style = ""  # TODO:
        pageTitle = "Exibir Documento"
        formTitle = "Documento"

    elif html_images.count == 0:
        pass
        # html has no images

    elif db_images.count == 0:
        pass
        # if any images are missing in the folder,
        # I can't help, no images found in db

    elif _prepare_img_files(html_images, db_images, img_path, section):
        body = img_change_src_path(body, img_path)

    return render_template(
        "./home/document.html.j2",
        **{
            "pageTitle": pageTitle,
            "formTitle": formTitle,
            "documentStyle": style,
            "documentBody": body,
        },
    )


# Errors --------------------------------------------------
# TODO: fix check unauthorized_handler
@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@bp_public.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@bp_public.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404

@bp_public.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500

# eof
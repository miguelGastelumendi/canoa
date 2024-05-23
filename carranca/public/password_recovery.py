# Equipe da Canoa -- 2024
# public\password_recovery.py
#
# mgd
# cSpell:ignore tmpl sqlalchemy passwordrecovery is_method_get passwordrecovery
"""
    *Password Recovery*
    Part of Public Authentication Processes
"""
from flask import  render_template, request
from carranca import db

import secrets

from ..helpers.route_helper import get_account_form_data, get_input_text, public_route, public_route_reset_password
from ..helpers.texts_helper import add_msg_error, add_msg_success
from ..helpers.error_helper import ModuleErrorCode
from ..helpers.email_helper import send_email

from .models import Users
from .forms import PasswordRecoveryForm
from  main import app_config


def do_password_recovery():
    template, is_get, texts = get_account_form_data('passwordrecovery')
    tmpl_form = PasswordRecoveryForm(request.form)

    send_to= '' if is_get else get_input_text('user_email').lower()
    user= None if is_get else Users.query.filter_by(email = send_to).first()

    if is_get:
        pass

    elif user == None:
        add_msg_error('emailNotRegistered', texts)

    else:
        task_code = ModuleErrorCode.PASSWORD_RECOVERY.value
        try:
            token= secrets.token_urlsafe()
            task_code+= 1
            url= f"http://{app_config.SERVER_EXT_ADDRESS}/{public_route(public_route_reset_password, token=token)}"
            task_code+= 1 #+2
            send_email(send_to, 'emailPasswordRecovery', {'url': url})
            task_code+= 1 #+3
            user.recover_email_token= token   # recover_email_token_at updated in trigger
            db.session.add(user)
            task_code+= 1 #+4
            db.session.commit()
            add_msg_success('emailSent', texts)
        except: #TODO: log
            add_msg_error('emailNotSent', texts, task_code)


    return render_template(template,
                            form= tmpl_form,
                            public_route= public_route,
                            **texts)

#eof
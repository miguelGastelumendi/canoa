# Equipe da Canoa -- 2024
# public\password_reset.py
#
# mgd
# cSpell:ignore tmpl sqlalchemy passwordrecovery is_method_get passwordrecovery
"""
    *Reset Password*
    Part of Public Authentication Processes
"""
from flask import render_template, request
from carranca import db

from ..helpers.py_helper import now, to_str
from ..helpers.pw_helper import hash_pass
from ..helpers.error_helper import ModuleErrorCode
from ..helpers.texts_helper import add_msg_error, add_msg_success
from ..helpers.route_helper import get_account_form_data, get_input_text, public_route_reset_password, public_route

from ..private.forms import NewPasswordForm

from .models import Users

def __is_token_valid(time_stamp, max: int) -> bool:
    """
    True when the number of days since issuance is less than
    or equal to `max`
    """
    days= (now() - time_stamp).days
    return 0 <= days <= max

def do_password_reset(token):
    template, is_get, texts = get_account_form_data(public_route_reset_password, 'rst_chg_password')
    token_str = to_str(token)
    password = '' if is_get else get_input_text('password')
    confirm_password = '' if is_get else get_input_text('confirm_password')

    # If you need the password pwd=  hash_pass(password);

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
        user_record_to_update = Users.query.filter_by(recover_email_token = token_str).first()
        if user_record_to_update == None:
            add_msg_error('invalidToken', texts)

        elif not __is_token_valid(user_record_to_update.recover_email_token_at, 5):
            add_msg_error('expiredToken', texts)

        else:
            # TODO: try/catch
            task_code = ModuleErrorCode.PASSWORD_RESET
            user_record_to_update.password = hash_pass(password)
            user_record_to_update.recover_email_token = None
            db.session.add(user_record_to_update)
            db.session.commit()
            add_msg_success('resetPwSuccess', texts)


    return render_template(
        template,
        form= tmpl_form,
        **texts,
        public_route= public_route,
    )
#eof
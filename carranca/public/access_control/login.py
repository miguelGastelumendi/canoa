"""
    *Login*
    Part of Public Access Control Processes

    Equipe da Canoa -- 2024
    mgd
"""
# cSpell:ignore tmpl sqlalchemy wtforms

from flask import render_template, request
from flask_login import login_user

from carranca.helpers.db_helper import persist_record

from ...helpers.py_helper import is_str_none_or_empty, now, to_str
from ...helpers.pw_helper import internal_logout, is_someone_logged, verify_pass
from ...helpers.texts_helper import add_msg_error
from ...helpers.error_helper import ModuleErrorCode
from ...helpers.route_helper import (
    home_route,
    redirect_to,
    init_form_vars,
    get_input_text,
    get_account_form_data,
)
from ..wtforms import LoginForm
from ..models import get_user_where


def login():
    from ...shared import db
    task_code = ModuleErrorCode.ACCESS_CONTROL_LOGIN.value
    tmpl_form, template, is_get, texts = init_form_vars()
    # TODO test, fake form?

    try:
        task_code += 1  # 1
        tmpl_form = LoginForm(request.form)
        task_code += 1  # 2
        template, is_get, texts = get_account_form_data('login')
        task_code += 1  # 3
        if is_get and is_someone_logged():
            internal_logout()
        elif is_get:
            pass
        else:
            task_code += 1  # 4
            username = get_input_text('username') #TODO tmpl_form
            task_code += 1  # 5
            password = get_input_text('password')
            task_code += 1  # 5
            search_for = to_str(username).lower()
            task_code += 1  # 7
            user = get_user_where(username_lower = search_for) # by uname
            task_code += 1  # 8
            user = get_user_where(email = search_for) if user is None else user #or by email
            task_code += 1  # 9
            if not user or not verify_pass(password, user.password):
                add_msg_error('userOrPwdIsWrong', texts)
            elif user.disabled:
                add_msg_error('userIsDisabled', texts)
            else:
                task_code += 1  # 10
                task_code += 1  # 11
                user.recover_email_token = None
                user.last_login_at = now()
                task_code += 1  # 12
                persist_record(db, user, task_code)

                remember_me = not is_str_none_or_empty(request.form.get('remember_me'))
                task_code += 1  # 13
                login_user(user, remember_me)
                task_code += 1  # 14
                return redirect_to(home_route())

    except Exception as e:
        msg = add_msg_error('errorLogin', texts, task_code)
        print(f"{e} -- {msg}.")

    return render_template(
        template,
        form=tmpl_form,
        **texts,
    )

# eof

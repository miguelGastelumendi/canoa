"""
    *Register a new user*
    Part of Public Access Control Processes

    Equipe da Canoa -- 2024
    mgd
"""
# cSpell:ignore tmpl sqlalchemy wtforms

from flask import render_template, request
from typing import Any
from carranca import db

from ...helpers.db_helper import persist_record
from ...helpers.pw_helper import internal_logout, is_someone_logged
from ...helpers.error_helper import ModuleErrorCode
from ...helpers.texts_helper import add_msg_success, add_msg_error
from ...helpers.route_helper import get_account_form_data, get_input_text, init_form_vars

from ..wtforms import RegisterForm
from ..models import Users


def do_register():
    def __exists_user_where(**kwargs: Any) -> bool:
        records = Users.query.filter_by(**kwargs)
        user = None if not records or records.count() == 0 else records.first()
        return user is not None

    task_code = ModuleErrorCode.ACCESS_CONTROL_REGISTER.value
    tmpl_form, template, is_get, texts = init_form_vars()
     # TODO test, fake form?

    try:
        task_code+= 1 # 1
        tmpl_form = RegisterForm(request.form)
        task_code+= 1 # 2
        template, is_get, texts = get_account_form_data('register')
        task_code+= 1 # 3
        if is_get and is_someone_logged():
            internal_logout()
        elif is_get:
            pass
        elif __exists_user_where(username_lower=get_input_text('username').lower()):
            add_msg_error('userAlreadyRegistered', texts)
        elif __exists_user_where(email=get_input_text('email').lower()):
            add_msg_error('emailAlreadyRegistered', texts)
        else:
            task_code+= 1 # 4
            user_record_to_insert = Users(**request.form)
            task_code+= 1 # 5
            persist_record(db, user_record_to_insert, task_code)
            task_code+= 1 # 6
            add_msg_success('welcome', texts)

    except Exception as e:
        msg= add_msg_error('errorRegister', texts, task_code)
        print(f"{e} -- {msg}.")

    return render_template(
        template,
        form=tmpl_form,
        **texts,
    )
# eof

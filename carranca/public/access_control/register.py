"""
    *Register a new user*
    Part of Public Access Control Processes

    Equipe da Canoa -- 2024
    mgd
"""

# cSpell:ignore tmpl sqlalchemy wtforms

from typing import Any
from flask import render_template, request

from ...app_context_vars import sidekick
from ...public.models import persist_user
from ...helpers.pw_helper import internal_logout, is_someone_logged
from ...helpers.error_helper import ModuleErrorCode
from ...helpers.route_helper import get_account_form_data, get_input_text, init_form_vars
from ...helpers.ui_texts_helper import add_msg_success, add_msg_error, add_msg_fatal

from ..wtforms import RegisterForm
from ..models import Users


def register():
    def __exists_user_where(**kwargs: Any) -> bool:
        records = Users.query.filter_by(**kwargs)
        user = None if not records or records.count() == 0 else records.first()
        return user is not None

    task_code = ModuleErrorCode.ACCESS_CONTROL_REGISTER.value
    tmpl_form, template, is_get, texts = init_form_vars()

    try:
        task_code += 1  # 1
        tmpl_form = RegisterForm(request.form)
        task_code += 1  # 2
        template, is_get, texts = get_account_form_data("register")
        user_name = "" if is_get else get_input_text("username")
        task_code += 1  # 3

        if is_get and is_someone_logged():
            internal_logout()
        elif is_get:
            pass
        elif __exists_user_where(username_lower=user_name.lower()):
            add_msg_error("userAlreadyRegistered", texts)
        elif __exists_user_where(email=get_input_text("email").lower()):
            add_msg_error("emailAlreadyRegistered", texts)
        elif not sidekick.config.DB_len_val_for_pw.check(get_input_text("password")):
            add_msg_error(
                "invalidPassword",
                texts,
                sidekick.config.DB_len_val_for_pw.min,
                sidekick.config.DB_len_val_for_pw.max,
            )
        elif not sidekick.config.DB_len_val_for_uname.check(user_name):
            add_msg_error(
                "invalidUserName",
                texts,
                sidekick.config.DB_len_val_for_uname.min,
                sidekick.config.DB_len_val_for_uname.max,
            )
        else:
            task_code += 1  # 4
            user_record_to_insert = Users(**request.form)
            task_code += 1  # 5
            persist_user(user_record_to_insert, task_code)
            task_code += 1  # 6
            add_msg_success("welcome", texts)

    except Exception as e:
        msg = add_msg_fatal("errorRegister", texts, task_code)
        sidekick.app_log.error(e)
        sidekick.app_log.debug(msg)

    return render_template(
        template,
        form=tmpl_form,
        **texts,
    )


# eof

"""
*Change Password*
Part of Private Access Control Processes

Equipe da Canoa -- 2024
mgd
"""

# cSpell:ignore tmpl wtforms

from flask import render_template, request
from flask_login import current_user

from ...models.public import persist_user
from ...helpers.pw_helper import internal_logout, hash_pass
from ...common.app_error_assistant import ModuleErrorCode
from ...helpers.ui_db_texts_helper import add_msg_error, add_msg_success, add_msg_final
from ...helpers.route_helper import (
    redirect_to,
    login_route,
    init_response_vars,
    get_input_text,
    get_account_response_data,
)
from ...common.app_context_vars import sidekick
from ...models.public import get_user_where
from ..wtforms import ChangePassword


def do_password_change():
    task_code = ModuleErrorCode.ACCESS_CONTROL_PW_CHANGE.value
    flask_form, tmpl_ffn, is_get, ui_texts = init_response_vars()

    try:
        task_code += 1  # 1
        tmpl_ffn, is_get, ui_texts = get_account_response_data("passwordChange", "password_reset_or_change")
        password = "" if is_get else get_input_text("password")
        task_code += 1  # 2
        confirm_password = "" if is_get else get_input_text("confirm_password")
        task_code += 1  # 3
        user = None if is_get else get_user_where(id=current_user.id)
        task_code += 1  # 4
        flask_form = ChangePassword(request.form)

        if is_get:
            pass
        elif not sidekick.config.DB_len_val_for_pw.check(password):
            add_msg_error(
                "invalidPassword",
                ui_texts,
                sidekick.config.DB_len_val_for_pw.min,
                sidekick.config.DB_len_val_for_pw.max,
            )
        elif password != confirm_password:
            add_msg_error("passwordsAreDifferent", ui_texts)
        elif user is None:
            internal_logout()
            return redirect_to(login_route())
        else:
            task_code += 1  # 5
            user.password = hash_pass(password)
            task_code += 1  # 6
            persist_user(user, task_code)
            task_code += 1  # 7
            add_msg_success("chgPwSuccess", ui_texts)
            task_code += 1  # 8
            internal_logout()

    except Exception as e:
        msg = add_msg_final("errorPasswordChange", ui_texts, task_code)
        sidekick.app_log.info(msg)
        sidekick.app_log.error(str(e))

    tmpl = render_template(tmpl_ffn, form=flask_form, **ui_texts)
    return tmpl


# eof

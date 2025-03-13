"""
    *Reset Password*
    Part of Public Access Control Processes

    Equipe da Canoa -- 2024
    mgd
"""

# cSpell:ignore tmpl wtforms passwordreset

from flask import render_template, request

from ...public.models import persist_user
from ...helpers.pw_helper import hash_pass
from ...helpers.py_helper import now, to_str
from ...helpers.error_helper import ModuleErrorCode
from ...helpers.ui_texts_helper import add_msg_error, add_msg_success, add_msg_fatal
from ...helpers.route_helper import (
    init_form_vars,
    get_input_text,
    get_account_form_data,
)
from ...private.wtforms import ChangePassword
from ..models import get_user_where


def password_reset(token):
    from ...common.app_context_vars import sidekick

    def __is_token_valid(time_stamp, max: int) -> bool:
        """
        True when the number of days since issuance is less than
        or equal to `max`
        """
        days = (now() - time_stamp).days
        return 0 <= days <= max

    task_code = ModuleErrorCode.ACCESS_CONTROL_PW_RESET.value
    tmpl_form, template, is_get, texts = init_form_vars()
    # TODO test, fake form?

    try:
        task_code += 1  # 1
        template, is_get, texts = get_account_form_data("passwordreset", "password_reset_or_change")
        token_str = to_str(token)
        password = "" if is_get else get_input_text("password")
        task_code += 1  # 2
        confirm_password = "" if is_get else get_input_text("confirm_password")

        # If you need the password pwd=  hash_pass(password);
        task_code += 1  # 3
        tmpl_form = ChangePassword(request.form)
        if len(token_str) < 12:
            add_msg_error("invalidToken", texts)
        elif is_get:
            pass
        elif not sidekick.config.DB_len_val_for_pw.check(password):
            add_msg_error("invalidPassword", texts)
        elif password != confirm_password:
            add_msg_error("passwordsAreDifferent", texts)
        else:
            task_code += 1  # 4
            record_to_update = get_user_where(recover_email_token=token_str)
            if record_to_update is None:
                add_msg_error("invalidToken", texts)
            elif not __is_token_valid(record_to_update.recover_email_token_at, 5):
                add_msg_error("expiredToken", texts)
            else:
                task_code += 1  # 5
                record_to_update.password = hash_pass(password)
                record_to_update.recover_email_token = None
                task_code += 1  # 6
                persist_user(record_to_update, task_code)
                add_msg_success("resetPwSuccess", texts)
    except Exception as e:
        msg = add_msg_fatal("errorPasswordReset", texts, task_code)
        sidekick.app_log.error(e)
        sidekick.app_log.debug(msg)

    return render_template(
        template,
        form=tmpl_form,
        **texts,
    )


# eof

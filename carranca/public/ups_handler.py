"""
*ups_handler*

    Handles exceptions and errors by displaying an HTML page.

Displays a html page to the user with
relevant information about the error.

TODO
It logs the error and sends an e-mail to the admin.

Equipe da Canoa -- 2025
mgd 2025-03-05
"""

# cSpell:ignore
import inspect
from typing import Optional, Tuple

from helpers.hints_helper import UI_Texts

# TO USE from flask import render_template

from ..helpers.pw_helper import internal_logout, is_someone_logged
from ..helpers.html_helper import icon_url
from ..helpers.route_helper import get_template_name
from ..config.local_ui_texts import local_ui_texts, local_form_texts
from ..helpers.ui_texts_helper import get_section, UITxtKey
from ..common.app_error_assistant import CanoeStumbled


#  --------------------
def ups_handler(
    error_code: int, user_msg: str, e: Exception, logout: bool = False
) -> Tuple[dict, str, UI_Texts]:
    from ..common.app_context_vars import logged_user, sidekick

    try:
        ui_texts = get_section(f"Ups-{error_code}")
    except:
        ui_texts = local_ui_texts(UITxtKey.Error.no_db_conn)

    if isinstance(e, CanoeStumbled):
        error_code = e.error_code
        error_msg = e.msg
    elif logged_user.is_power if logged_user else False:
        error_msg = str(e)
    else:
        error_msg = None

    context_texts = {
        UITxtKey.Msg.warn: user_msg,
        UITxtKey.Msg.error: error_msg,
        UITxtKey.Form.msg_only: True,
        UITxtKey.Form.icon: icon_url("icons", "ups_handler.svg"),
        UITxtKey.Error.code: error_code,
        UITxtKey.Error.where: inspect.stack()[1].function,
        UITxtKey.Error.http_code: 500,
    }

    for key, value in context_texts.items():
        if key not in ui_texts:
            ui_texts[key] = value

    for key, value in local_form_texts().items():
        if key not in ui_texts:
            ui_texts[key] = value

    # TODO: send email
    if logout and is_someone_logged():
        internal_logout()

    ups_template = get_template_name("ups_page", "home")

    sidekick.app_log.error(e)
    sidekick.app_log.debug(error_msg)

    return {}, ups_template, ui_texts


# eof

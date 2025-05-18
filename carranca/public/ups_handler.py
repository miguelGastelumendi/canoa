"""
*ups_handler*

    Handles exceptions and errors by displaying an HTML page.

Displays a html page to the user with
relevant information about the error.

    Ups Files
    ---------
    /public/ups_handler.py
    /static/icons/ups_handler.svg
    /templates/home/ups_page.html.j2

TODO
It logs the error and sends an e-mail to the admin.

Equipe da Canoa -- 2025
mgd 2025-03-05
"""

# cSpell:ignore
import inspect
from typing import Tuple

# TO USE from flask import render_template

from ..helpers.pw_helper import internal_logout, is_someone_logged
from ..helpers.html_helper import icon_url
from ..helpers.types_helper import ui_db_texts
from ..helpers.route_helper import get_template_name
from ..config.local_ui_texts import local_ui_texts, local_form_texts
from ..helpers.ui_db_texts_helper import get_section, UITextsKeys
from ..common.app_error_assistant import AppStumbled


#  --------------------
def ups_handler(
    error_code: int, user_msg: str, e: Exception, logout: bool = None
) -> Tuple[dict, str, ui_db_texts]:
    from ..common.app_context_vars import app_user, sidekick

    try:
        ui_texts = get_section(f"Ups-{error_code}")
    except:
        ui_texts = local_ui_texts(UITextsKeys.Fatal.no_db_conn)

    if isinstance(e, AppStumbled):
        error_code = e.error_code
        error_msg = e.msg
        logout = e.logout
    elif app_user.is_power if app_user else False:
        error_msg = str(e)
    else:
        error_msg = None

    # Get the name of the caller function
    caller_function = inspect.stack()[1].function

    context_texts = {
        UITextsKeys.Msg.warn: user_msg,
        UITextsKeys.Msg.error: error_msg,
        UITextsKeys.Form.msg_only: True,
        UITextsKeys.Form.icon_url: icon_url("icons", "ups_handler.svg"),
        UITextsKeys.Form.btn_close: "Entendi",  # TODO: uiTexts
        UITextsKeys.Fatal.code: error_code,
        UITextsKeys.Fatal.where: caller_function,
        UITextsKeys.Fatal.http_code: 500,
    }

    for key, value in context_texts.items():
        # override if key not in ui_texts:
        ui_texts[key] = value

    for key, value in local_form_texts().items():
        if key not in ui_texts:
            ui_texts[key] = value

    # TODO: send email
    if (False if logout is None else logout) and is_someone_logged():
        internal_logout()

    ups_template = get_template_name("ups_page", "home")

    sidekick.app_log.error(e)
    sidekick.app_log.debug(error_msg)

    return {}, ups_template, ui_texts


# eof

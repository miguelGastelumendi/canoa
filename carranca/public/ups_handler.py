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
from os import path
from typing import Tuple, Optional

# TO USE from flask import render_template

from ..helpers.pw_helper import internal_logout, is_someone_logged
from ..helpers.html_helper import icon_url
from ..helpers.types_helper import UiDbTexts
from ..helpers.route_helper import get_tmpl_full_file_name
from ..config.local_ui_texts import local_ui_texts, local_form_texts
from ..helpers.ui_db_texts_helper import get_section, UITextsKeys
from ..common.app_error_assistant import AppStumbled


#  --------------------
def ups_handler(
    error_code: int, user_msg: str, e: Optional[Exception] = None, logout: bool = False
) -> Tuple[dict, str, UiDbTexts]:
    from ..common.app_context_vars import app_user, sidekick

    try:
        ui_texts = get_section(f"Ups-{error_code}")
    except:
        ui_texts = local_ui_texts(UITextsKeys.Fatal.no_db_conn)

    tech_msg = None
    if not e:
        error_msg = None  # no error, just a message for the user
    elif isinstance(e, AppStumbled):
        error_code = e.error_code
        error_msg = e.msg
        logout = e.logout
        tech_msg = e.tech_info if e.tech_info else sidekick.log_filename
    elif app_user.is_power if app_user else False:
        error_msg = str(e)
    else:  # don't show to the common user a strange str
        error_msg = None

    # Get the name of the caller function
    caller_function = inspect.stack()[1].function

    # default texts that can be use in the form (see ups_page)
    context_texts = {
        UITextsKeys.Msg.tech: tech_msg,
        UITextsKeys.Msg.warn: user_msg,
        UITextsKeys.Msg.error: error_msg,
        UITextsKeys.Msg.display_only_msg: True,
        UITextsKeys.Fatal.code: error_code,
        UITextsKeys.Fatal.where: caller_function,
        UITextsKeys.Fatal.http_code: 500,
    }

    # add `context texts` if not found in section: "Ups-{error_code}"
    for key, value in context_texts.items():
        # override if key not in ui_texts:
        if key not in ui_texts:
            ui_texts[key] = value

    # add `local texts` if not found in "context_texts" nor in "Ups-{error_code}"
    for key, value in local_form_texts().items():
        if key not in ui_texts:
            ui_texts[key] = value

    # set the url for the icon IF a file name exists
    if (file:= ui_texts.get(UITextsKeys.Form.icon_file)) and not ui_texts.get(UITextsKeys.Form.icon_url):
        ui_texts[UITextsKeys.Form.icon_url] = icon_url("icons", file)

    # TODO: send email
    if logout and is_someone_logged():
        internal_logout()

    ups_template = get_tmpl_full_file_name("ups_page", "home")

    sidekick.app_log.error(e)
    sidekick.app_log.debug(error_msg)

    return {}, ups_template, ui_texts


# eof

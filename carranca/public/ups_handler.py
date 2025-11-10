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

import html
import inspect
from typing import Tuple, Optional, Any

from ..common.UIDBTexts import UIDBTexts
from ..helpers.py_helper import is_str_none_or_empty
from ..helpers.pw_helper import internal_logout, is_someone_logged
from ..helpers.html_helper import icon_url
from ..helpers.route_helper import get_tmpl_full_file_name
from ..config.local_ui_texts import AuxTexts, local_ui_texts, local_form_texts
from ..helpers.ui_db_texts_helper import get_section, UITextsKeys
from ..common.app_error_assistant import AppStumbled


#  --------------------
def ups_handler(
    error_code: int, user_msg: str, e: Optional[Exception] = None, logout: bool = False
) -> Tuple[dict, str, UIDBTexts]:
    from ..common.app_context_vars import app_user, sidekick

    try:
        ui_texts = get_section(f"Ups-{error_code}")
    except:
        ui_texts = local_ui_texts(UITextsKeys.Fatal.no_db_conn)


    def _get_tech_msg():
        tech_msg = getattr(e, "tech_info", '')
        return tech_msg if tech_msg else local_ui_texts(AuxTexts.section)[AuxTexts.techIntro].format(sidekick.log_filename)

    tech_msg = ''
    error_msg = ''
    if not e:
        error_msg = ''  # no error, just a message for the user
    elif isinstance(e, AppStumbled):
        error_code = e.error_code
        error_msg = e.msg
        logout = e.logout
        tech_msg = _get_tech_msg()
    elif app_user.is_power if app_user else False:
        error_msg = html.escape(str(e))
        tech_msg = _get_tech_msg()
    else: # common user with error: display user_msg & log_filename
        tech_msg = _get_tech_msg()


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

    def _should_update(key: str, value: Any) -> bool:
        return not is_str_none_or_empty(value) and (key not in ui_texts or is_str_none_or_empty(ui_texts.get(key)))

    # Add `context_texts` if the key is missing from ui_texts or its value is empty.
    for key, value in context_texts.items():
        if _should_update(key, value):
            ui_texts[key] = value

    # Add `local_form_texts` if the key is missing or its value is empty.
    for key, value in local_form_texts().items():
        if _should_update(key, value):
            ui_texts[key] = value

    # set the url for the icon IF a file name exists
    if (file_name:= ui_texts.get(UITextsKeys.Form.icon_file)) and not ui_texts.get(UITextsKeys.Form.icon_url):
        ui_texts[UITextsKeys.Form.icon_url] = icon_url("icons", file_name)

    # TODO: send email
    if logout and is_someone_logged():
        internal_logout()

    ups_template = get_tmpl_full_file_name("ups_page", "home")

    sidekick.app_log.error(e)
    sidekick.app_log.debug(error_msg)

    return {}, ups_template, UIDBTexts(ui_texts, False)

# eof

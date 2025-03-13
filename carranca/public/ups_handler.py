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
from flask import render_template
from helpers.pw_helper import internal_logout, is_someone_logged
from helpers.ui_texts_helper import get_section, ui_msg_only, ui_msg_exception, ui_msg_info, ui_icon_file_url

#  --------------------
def ups_handler( task_code: int, msg_exception: str, msg_info: str, logout: bool = False ): #, user_msg: str):
    ui_texts = get_section("UpsTexts")

    ui_texts[ui_msg_only] = False
    ui_texts[ui_msg_info] = msg_info
    ui_texts[ui_msg_exception] = msg_exception
    ui_texts[ui_icon_file_url] = 'home/ups_handler.svg'

    context_texts = {
        "ups_task_code": task_code,
        "ups_offending_def": inspect.stack()[1].function,
        "ups_http_code": 500,
    }

    for key, value in context_texts.items():
        if key not in ui_texts:
            ui_texts[key] = value

    if logout and is_someone_logged():
        internal_logout()

    return render_template("home/ups_page.html", **ui_texts)


# eof

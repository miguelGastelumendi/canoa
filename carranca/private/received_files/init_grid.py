"""
User's Received Files's Management

Grid Initialization

Equipe da Canoa -- 2025
mgd 2025-01-14 & 03-18
"""

# cSpell: ignore mgmt tmpl samp rqst dnld rprt


from flask import render_template

from ...public.ups_handler import ups_handler
from ...private.roles_abbr import RolesAbbr
from ...helpers.route_helper import get_private_form_data, init_form_vars
from ...helpers.js_grid_helper import js_grid_constants
from ...helpers.ui_texts_helper import add_msg_fatal
from ...common.app_error_assistant import ModuleErrorCode
from ...common.app_context_vars import sidekick, logged_user

from .constants import DNLD_R, DNLD_F
from .fetch_users import fetch_user_s
from .fetch_records import fetch_record_s


def init_grid() -> str:
    task_code = ModuleErrorCode.RECEIVED_FILES_MGMT.value
    _, template, is_get, ui_texts = init_form_vars()

    tmpl = ""
    if not is_get:
        return ""  # TODO: error
    try:
        task_code += 1  # 1
        template, is_get, ui_texts = get_private_form_data("receivedFilesMgmt")

        task_code += 1  # 2
        files_rec, _, _ = fetch_record_s(ui_texts["itemNone"], None)
        users_list = []
        task_code += 1  # 3
        if logged_user.is_power:
            task_code += 1  # 4
            users = fetch_user_s()
            users_list = [f"{user.user_name} ({user.files_count})" for user in users]
        else:
            task_code += 1  # 4

        # TODO check empty received_files
        task_code += 1  # 5
        col_names = files_rec[0].keys() if files_rec else []
        grid_const, _ = js_grid_constants(ui_texts["colMetaInfo"], col_names)
        grid_const["dnld_R"] = DNLD_R
        grid_const["dnld_F"] = DNLD_F
        w = max(len(ui_texts["btnDwnLoadFile"]), len(ui_texts["btnDwnLoadRprt"])) + 1
        sw = "width:{}ch"
        grid_const["btn_width"] = sw.format(w)
        lw = max(len(s) for s in users_list)
        grid_const["sel_width"] = sw.format(min(w, lw))
        grid_const["user_is_power"] = logged_user.is_power
        task_code += 1  # 6
        tmpl = render_template(
            template, files_rec=files_rec.to_json(), users_list=users_list, **grid_const, **ui_texts
        )

    except Exception as e:
        msg = add_msg_fatal("gridException", ui_texts, task_code)
        _, template, ui_texts = ups_handler(task_code, msg, e, False)
        tmpl = render_template(template, **ui_texts)
        sidekick.app_log.error(e)
        sidekick.display.error(msg)

    return tmpl


# eof

"""
User's Received Files's Management

Grid Initialization

Equipe da Canoa -- 2025
mgd 2025-01-14 & 03-18
"""

# cSpell: ignore mgmt tmpl samp rqst dnld rprt


from flask import render_template
from flask_login import current_user

from ...public.ups_handler import ups_handler
from ...private.roles_abbr import RolesAbbr
from ...helpers.route_helper import get_private_form_data, init_form_vars
from ...helpers.js_grid_helper import js_grid_constants
from ...helpers.ui_texts_helper import UITxtKey, add_msg_fatal
from ...common.app_error_assistant import ModuleErrorCode
from ...common.app_context_vars import sidekick, logged_user

from .constants import DNLD_R, DNLD_F
from .fetch_users import fetch_user_s
from .fetch_records import fetch_record_s, ALL_RECS


def init_grid(for_user: int) -> str:
    task_code = ModuleErrorCode.RECEIVED_FILES_MGMT.value
    _, template, is_get, ui_texts = init_form_vars()

    if not is_get:
        return ""  # TODO: a generic ups Bad Request

    tmpl = ""
    try:
        task_code += 1  # 1
        template, is_get, ui_texts = get_private_form_data("receivedFilesMgmt")
        task_code += 1  # 2
        if logged_user.is_power:
            task_code += 1  # 3
            users = fetch_user_s()
            task_code += 1  # 4
            request_user = next((user for user in users if user.user_id == for_user), None)
            # TODO: if request_user is none Ups!
            task_code += 1  # 5
            users_list = [
                (user.user_id, f"{user.user_name} ({user.files_count})")
                for user in users
                if user.user_name != request_user.user_name
            ]
            task_code += 1  # 6
            ui_texts[UITxtKey.Form.title] = ui_texts[UITxtKey.Form.title + "Power"].format(
                request_user.user_name
            )
            user_id = request_user.user_id
        else:  # ignore `for_user`
            task_code += 4  # 6
            users_list = []
            user_id = current_user.id

        # TODO check empty received_files
        task_code += 1  # 7
        files_rec, _, _ = fetch_record_s(ui_texts["itemNone"], ALL_RECS, user_id)
        col_names = files_rec[0].keys() if files_rec else []
        task_code += 1  # 8
        grid_const, _ = js_grid_constants(ui_texts["colMetaInfo"], col_names)

        task_code += 1  # 9
        grid_const["user_is_power"] = logged_user.is_power
        grid_const["dnld_R"] = DNLD_R
        grid_const["dnld_F"] = DNLD_F
        task_code += 1  # 10
        bw = max(len(ui_texts["btnDwnLoadFile"]), len(ui_texts["btnDwnLoadRprt"])) + 1
        sw = "width:{}ch"
        grid_const["btn_width"] = sw.format(bw)
        lw = max(len(s) for s in users_list) if users_list else 0
        grid_const["sel_width"] = sw.format(max(bw, lw))
        grid_const["sel_id"] = "usrListID"

        task_code += 1  # 11
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

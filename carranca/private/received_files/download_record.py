"""
User's Received Files's Management

    user request to download one of the files
    he has sent for validation or it's generated report.

Equipe da Canoa -- 2025
mgd 2025-01-14 03-18
"""

# cSpell: ignore samp rqst dnld rprt

from os import path
from flask import send_file, abort, request, Response

from .constants import DNLD_R, DNLD_F
from .fetch_records import fetch_record_s, IGNORE_USER

from ...helpers.js_consts_helper import js_form_sec_check, js_form_cargo_id
from ...helpers.file_helper import change_file_ext
from ...helpers.route_helper import get_private_response_data, init_response_vars, is_str_none_or_empty
from ...helpers.ui_db_texts_helper import UITextsKeys, add_msg_error
from ...common.app_error_assistant import ModuleErrorCode, AppStumbled


def download_rec() -> Response | None:
    task_code = ModuleErrorCode.RECEIVED_FILES_MGMT.value
    _, _, is_get, ui_texts = init_response_vars()

    if not is_get:
        return None  # TODO: error

    file_response = None
    try:
        task_code += 1  # 1
        _, is_get, ui_texts = get_private_response_data("receivedFilesMgmt")

        task_code += 1  # 2
        rqst = request.form.get(js_form_cargo_id)
        rec_id, rec_type = rqst[:-1], rqst[-1]
        if not is_str_none_or_empty(msg_key:= js_form_sec_check()):
            task_code += 1  # 3
            msg = add_msg_error(msg_key, ui_texts)
            raise AppStumbled(msg, task_code, True, True)
        elif not (rec_id.isdigit() and rec_type in [DNLD_R, DNLD_F]):
            task_code += 2  # 4
            msg = add_msg_error("secKeyViolation", ui_texts)
            raise AppStumbled(msg, task_code, True, True)
        else:
            task_code += 3  # 5
            no_sep = ui_texts["itemNone"]
            received_files, download_file_name, report_ext = fetch_record_s(no_sep, rec_id, IGNORE_USER)
            if rec_type == DNLD_R:
                download_file_name = change_file_ext(download_file_name, report_ext)

            if len(received_files) != 1:
                ui_texts[UITextsKeys.Msg.error] = ui_texts["noRecord"]
            elif path.isfile(download_file_name):
                file_response = send_file(download_file_name)
            else:  # just deleted :-(
                ui_texts[UITextsKeys.Msg.error] = ui_texts["fileNotFound"]



    except Exception as e:
        # TODO:
        print(e)
        return abort(404, description="File not found")

    return file_response


# eof

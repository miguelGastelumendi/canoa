"""
    User's Received Files's Management

    Equipe da Canoa -- 2025
    mgd 2025-01-14
"""

# cSpell: ignore mgmt tmpl samp rqst

import json
from os import path
from flask import render_template

from .models import ReceivedFiles, MgmtUserSep
from .grid_texts import grid_id
from ..common.app_context_vars import sidekick, logged_user
from ..config.config_validate_process import ValidateProcessConfig

from ..helpers.db_helper import DBRecords
from ..helpers.user_helper import UserFolders
from ..helpers.file_helper import change_file_ext
from ..helpers.error_helper import ModuleErrorCode
from ..helpers.route_helper import get_private_form_data, init_form_vars
from ..helpers.ui_texts_helper import (
    add_msg_fatal,
    ui_msg_error,
    ui_msg_success,
    ui_msg_exception,
)


def received_files_fetch(no_sep: str, rec_id: int) -> DBRecords:
    """Fetch received files records from the view vw_user_data_files

    :param no_sep: str: text to show when the record has an empty SEP
    :param rec_id: int: record id to fetch
        When rec_id is None, fetch all records for the logged user
        otherwise, fetch the record with the given id and returns the file full_name
    :return: DBRecords: records fetched	and the last record's file full_name

    """

    user_id = None if rec_id or logged_user is None else logged_user.id
    # todo user c//if user.

    received_files = ReceivedFiles.get_user_records(id=rec_id, user_id=user_id)
    received_rows = DBRecords(received_files.table_name)
    if not (received_files is None or len(received_files) == 0):
        uf = UserFolders()
        report_ext = ValidateProcessConfig(False).output_file.ext

        for record in received_files:
            folder = uf.uploaded if record.file_origin == "L" else uf.downloaded
            file_full_name = path.join(folder, logged_user.folder, record.stored_file_name)
            # Copy specific fields to a new object 'row'
            row = {
                "id": record.id,
                "file_found": path.isfile(file_full_name),
                "report_found": path.isfile(change_file_ext(file_full_name, report_ext)),
                "sep": record.sep_fullname if record.sep_fullname else no_sep,
                "file_name": change_file_ext(record.file_name),
                "user_name": record.user_name,
                "receipt": record.user_receipt,
                "when": record.submitted_at,
                "errors": record.report_errors,
                "warns": record.report_warns,
            }
            received_rows.append(row)

    return received_rows, change_file_ext(file_full_name, "")


def received_files_grid() -> str:

    task_code = ModuleErrorCode.RECEIVED_FILES_MGMT.value
    _, template, is_get, uiTexts = init_form_vars()

    if not is_get:
        return ""  # TODO: error

    try:
        task_code += 1  # 1
        template, is_get, uiTexts = get_private_form_data("receivedFilesMgmt")

        task_code += 1  # 2
        # TODO: create a real key with user_id and datetime
        js_grid_sec_value = "7298kaj0fk9dl-sd=)0y"
        # uiTexts keys used in JavaScript
        js_grid_sec_key = "gridSecKey"
        js_grid_rsp = "gridRsp"
        js_grid_submit_id = "gridSubmitID"

        # py/js communication
        uiTexts[js_grid_rsp] = js_grid_rsp
        uiTexts["gridSecValue"] = js_grid_sec_value
        uiTexts[js_grid_submit_id] = js_grid_submit_id
        uiTexts[js_grid_sec_key] = js_grid_sec_key

        task_code += 1  # 3
        col_headers = json.loads(uiTexts["colHeaders"])

        task_code += 1  # 4
        received_files, _ = received_files_fetch(uiTexts["itemNone"], None)

        task_code += 1  # 5
        col_names = received_files[0].keys() if received_files else []

        task_code += 1  # 6

        # if set(col_names.keys()).issubset(col_headers.keys()):
        #     print("All keys in col_names are present in col_headers")
        #     result = [{"n": key, "h": col_headers[key]} for key in col_names]
        #     print(result)
        # else:
        #     print("Not all keys in col_names are present in col_headers")
        #     missing_keys = set(col_names.keys()) - set(col_headers.keys())
        #     print(f"Missing keys: {missing_keys}")

        # uiTexts["colData"] = [{"n": key, "h": col_headers[key]} for key in col_names]
        uiTexts["colData"] = [{"n": key, "h": col_headers[key]} for key in col_headers]

    except Exception as e:
        msg = add_msg_fatal("gridException", uiTexts, task_code)
        sidekick.app_log.error(e)
        sidekick.display.error(msg)
        # Todo error with users_sep,,, not ready

    tmpl = render_template(template, rec_files=received_files.to_json(), gridID=grid_id, **uiTexts)
    return tmpl


def received_file_get() -> str:  # | File:

    from flask import send_file, abort, request

    task_code = ModuleErrorCode.RECEIVED_FILES_MGMT.value
    _, template, is_get, uiTexts = init_form_vars()

    if not is_get:
        return ""  # TODO: error

    try:
        task_code += 1  # 1
        template, is_get, uiTexts = get_private_form_data("receivedFilesMgmt")

        task_code += 1  # 2
        # TODO: create a real key with user_id and datetime
        js_grid_sec_value = "7298kaj0fk9dl-sd=)0y"
        # uiTexts keys used in JavaScript
        js_grid_sec_key = "gridSecKey"
        js_grid_rsp = "gridRsp"
        js_grid_submit_id = "gridSubmitID"

        # file_name = file_info
        # F = send_file(file_name)
        rqst = request.form.get(js_grid_rsp)
        rec_id, rec_type = rqst[:-1], rqst[-1]
        if request.form.get(js_grid_sec_key) != js_grid_sec_value:
            task_code += 2  # 7
            uiTexts[ui_msg_exception] = uiTexts["secKeyViolation"]
            # TODO internal_logout()
        elif not (rec_id.isdigit() and rec_type in ["Z", "P"]):
            uiTexts[ui_msg_exception] = uiTexts["secKeyViolation"]  # TODO
        else:
            task_code += 1  # 4
            received_files, file_full_name = received_files_fetch(uiTexts["itemNone"], rec_id)
            file_name = file_full_name + ".zip" if (rec_type == "Z") else ".pdf"
            if received_files.count != 1:
                uiTexts[ui_msg_error] = uiTexts["noRecord"]
            elif path.isfile(file_name):
                F = send_file(file_name)
            else:
                uiTexts[ui_msg_error] = uiTexts["fileNotFound"]

    except Exception as e:
        print(e)
        return abort(404, description="File not found")

    return F


# eof

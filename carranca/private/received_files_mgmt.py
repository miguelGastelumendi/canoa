"""
    User's Received Files's Management

    Equipe da Canoa -- 2025
    mgd 2025-01-14
"""

# cSpell: ignore mgmt tmpl samp

import json
from flask import render_template

from ..Sidekick import sidekick
from ..helpers.db_helper import TableEmpty, TableRecords
from ..helpers.py_helper import is_str_none_or_empty
from ..helpers.error_helper import ModuleErrorCode
from ..helpers.route_helper import get_private_form_data, init_form_vars
from ..helpers.hints_helper import UI_Texts
from ..helpers.ui_texts_helper import (
    add_msg_fatal,
    format_ui_item,
    ui_DialogIcon,
    ui_msg_error,
    ui_msg_success,
    ui_msg_exception,
)
from .models import ReceivedFiles
from .logged_user import logged_user


def received_files_get() -> TableRecords:

    user_id = None if logged_user is None else logged_user.id
    # todo user c//if user.

    received_files: TableRecords = ReceivedFiles.get_user_records(user_id)
    return received_files


def received_files_grid() -> str:

    task_code = ModuleErrorCode.RECEIVED_FILES_MGMT.value
    _, template, is_get, uiTexts = init_form_vars()

    users_sep = TableEmpty
    sep_fullname_list = []

    try:
        task_code += 1  # 1
        template, is_get, uiTexts = get_private_form_data("receivedFilesMgmt")

        task_code += 1  # 2
        # TODO: create a real key with user_id and datetime
        js_grid_sec_value = "7298kaj0fk9dl-sd=)0x"
        # uiTexts keys used in JavaScript
        js_grid_sec_key = "gridSecKey"
        js_grid_rsp = "gridRsp"
        js_grid_submit_id = "gridSubmitID"

        # py/js communication
        uiTexts[js_grid_rsp] = js_grid_rsp
        uiTexts["gridSecValue"] = js_grid_sec_value
        uiTexts[js_grid_submit_id] = js_grid_submit_id
        uiTexts[js_grid_sec_key] = js_grid_sec_key

        uiTexts[ui_DialogIcon] = SepIconConfig.set_url(SepIconConfig.none_file)

        task_code += 1  # 3
        colData = json.loads(uiTexts["colData"])
        task_code += 1  # 4
        # grid columns, colData & colNames *must* match in length.
        colNames = ["user_id", "file_url", "user_name", "scm_sep_curr", "scm_sep_new", "when"]
        task_code += 1  # 5
        # Rewrite it in an easier way to express it in js: colName: colHeader
        uiTexts["colData"] = [{"n": key, "h": colData[key]} for key in colNames]

        def __get_grid_data():
            users_sep, sep_list, msg_error = MgmtUserSep.get_grid_view(uiTexts["itemNone"])
            sep_fullname_list = [sep["fullname"] for sep in sep_list]
            return users_sep, sep_fullname_list, msg_error

        if is_get:
            task_code += 1  # 6
            users_sep, sep_fullname_list, uiTexts[ui_msg_error] = __get_grid_data()
        elif request.form.get(js_grid_sec_key) != js_grid_sec_value:
            task_code += 2  # 7
            uiTexts[ui_msg_exception] = uiTexts["secKeyViolation"]
            internal_logout()
        else:
            task_code += 3
            txtGridResponse = request.form.get(js_grid_rsp)
            msg_success, msg_error, task_code = _save_and_email(txtGridResponse, uiTexts, task_code)
            task_code += 1
            users_sep, sep_fullname_list, msg_error_read = __get_grid_data()
            if is_str_none_or_empty(msg_error) and is_str_none_or_empty(msg_error_read):
                uiTexts[ui_msg_success] = msg_success
            elif is_str_none_or_empty(msg_error):
                uiTexts[ui_msg_error] = msg_error_read
            else:
                uiTexts[ui_msg_error] = msg_error

    except Exception as e:
        msg = add_msg_fatal("gridException", uiTexts, task_code)
        sidekick.app_log.error(e)
        sidekick.display.error(msg)
        # Todo error with users_sep,,, not ready

    tmpl = render_template(template, usersSep=users_sep, sepList=sep_fullname_list, **uiTexts)
    return tmpl

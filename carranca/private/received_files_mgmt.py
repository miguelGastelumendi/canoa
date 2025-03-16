"""
User's Received Files's Management

Equipe da Canoa -- 2025
mgd 2025-01-14
"""

# cSpell: ignore mgmt tmpl samp rqst dnld

from os import path
from flask import render_template, send_file, abort, request, Response

from .models import ReceivedFiles
from ..common.app_context_vars import sidekick, logged_user
from ..config.config_validate_process import ValidateProcessConfig

from ..helpers.db_helper import DBRecords
from ..helpers.user_helper import UserFolders
from ..helpers.js_grid_helper import (
    js_grid_constants,
    js_grid_sec_key,
    js_grid_rsp,
    js_grid_sec_value,
)
from ..helpers.file_helper import change_file_ext
from ..common.app_error_assistant import ModuleErrorCode
from ..helpers.route_helper import get_private_form_data, init_form_vars
from ..helpers.ui_texts_helper import UITxtKey, add_msg_fatal

# Don't repeat constants
dnld_R = "R"  # Report
dnld_F = "F"  # File


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
    file_full_name = None
    report_ext = ValidateProcessConfig(False).output_file.ext
    if not (received_files is None or len(received_files) == 0):
        uf = UserFolders()

        for record in received_files:
            folder = uf.uploaded if record.file_origin == "L" else uf.downloaded
            file_full_name = path.join(
                folder, logged_user.folder, record.stored_file_name
            )
            # Copy specific fields to a new object 'row'
            row = {
                "id": record.id,
                "data_f_found": path.isfile(file_full_name),  # data_file was found
                "report_found": path.isfile(
                    change_file_ext(file_full_name, report_ext)
                ),
                "sep": record.sep_fullname if record.sep_fullname else no_sep,
                "file_name": change_file_ext(record.file_name),
                "user_name": record.user_name,
                "receipt": record.user_receipt,
                "when": record.submitted_at,
                "errors": record.report_errors,
                "warns": record.report_warns,
            }
            received_rows.append(row)

    return received_rows, file_full_name, report_ext


def received_files_grid() -> str:
    task_code = ModuleErrorCode.RECEIVED_FILES_MGMT.value
    _, template, is_get, ui_texts = init_form_vars()

    tmpl = ""
    if not is_get:
        return ""  # TODO: error
    try:
        task_code += 1  # 1
        template, is_get, ui_texts = get_private_form_data("receivedFilesMgmt")

        task_code += 1  # 2
        received_files, _, _ = received_files_fetch(ui_texts["itemNone"], None)

        # TODO check empty received_files
        col_names = received_files[0].keys() if received_files else []
        grid_const, err_code = js_grid_constants(ui_texts["colMetaInfo"], col_names)
        grid_const["dnld_R"] = dnld_R
        grid_const["dnld_F"] = dnld_F
        grid_const["grid_user_is_adm"] = str(True).lower()  # js bool TODO: logged_user.

        task_code += 1  # 3
        tmpl = render_template(
            template, rec_files=received_files.to_json(), **grid_const, **ui_texts
        )

    except Exception as e:
        msg = add_msg_fatal("gridException", ui_texts, task_code)
        sidekick.app_log.error(e)
        sidekick.display.error(msg)

    return tmpl


def received_file_get() -> str | Response:
    task_code = ModuleErrorCode.RECEIVED_FILES_MGMT.value
    _, template, is_get, ui_texts = init_form_vars()

    if not is_get:
        return ""  # TODO: error

    try:
        task_code += 1  # 1
        _, is_get, ui_texts = get_private_form_data("receivedFilesMgmt")

        task_code += 1  # 2
        rqst = request.form.get(js_grid_rsp)
        rec_id, rec_type = rqst[:-1], rqst[-1]
        if request.form.get(js_grid_sec_key) != js_grid_sec_value:
            task_code += 2  # 7
            ui_texts[UITxtKey.Msg.exception] = ui_texts["secKeyViolation"]
            # TODO internal_logout()
        elif not (rec_id.isdigit() and rec_type in [dnld_R, dnld_F]):
            ui_texts[UITxtKey.Msg.exception] = ui_texts["secKeyViolation"]  # TODO
        else:
            task_code += 1  # 4
            no_sep = ui_texts["itemNone"]
            received_files, download_file_name, report_ext = received_files_fetch(
                no_sep, rec_id
            )
            if rec_type == dnld_R:
                download_file_name = change_file_ext(download_file_name, report_ext)

            if received_files.count != 1:
                ui_texts[UITxtKey.Msg.error] = ui_texts["noRecord"]
            elif path.isfile(download_file_name):
                F = send_file(download_file_name)
            else:  # just deleted :-(
                ui_texts[UITxtKey.Msg.error] = ui_texts["fileNotFound"]

    except Exception as e:
        print(e)
        return abort(404, description="File not found")

    return F


# eof

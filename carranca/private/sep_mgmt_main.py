"""
SEP Management and User assignment

NB: SEP is an old acronym for
    "Setor Estratégico de Planejamento" (Strategic Planning Sector)
    so it was kept here until we find a better name.

Equipe da Canoa -- 2024
mgd 2024-10-09, 2025-04-09  v 1.0 One user <-> one SEP
mgd 2025-04-03              v 2.0 One user -> several SEP
mgd 2025-05-09                    Split file into sep_mgmt_email.py and sep_mgmt_save.py
"""

# cSpell: ignore mgmt tmpl samp

import json
from flask import render_template, request
from typing import Tuple, List

from .models import MgmtSepUser
from .sep_icon import icon_prepare_for_html
from .SepIconConfig import SepIconConfig

from ..public.ups_handler import ups_handler
from ..common.app_error_assistant import ModuleErrorCode

from ..helpers.py_helper import is_str_none_or_empty
from ..helpers.db_helper import DBRecords, ListOfDBRecords, try_get_mgd_msg
from ..helpers.user_helper import get_batch_code
from ..helpers.route_helper import get_private_form_data, init_form_vars
from ..helpers.types_helper import ui_db_texts, sep_mgmt_rtn
from ..helpers.js_grid_helper import js_grid_constants, js_grid_sec_key, js_grid_rsp, js_grid_sec_value
from ..helpers.ui_db_texts_helper import add_msg_fatal, UITextsKeys

from .sep_mgmt_save import save_data
from .sep_mgmt_email import send_email


def do_sep_mgmt() -> str:
    task_code = ModuleErrorCode.SEP_MGMT.value
    _, template, is_get, ui_texts = init_form_vars()

    users_sep: ListOfDBRecords = []
    sep_fullname_list = []
    msg_error: str = None
    tmpl = ""
    try:
        task_code += 1  # 1
        template, is_get, ui_texts = get_private_form_data("sepMgmt")

        task_code += 1  # 2
        ui_texts[UITextsKeys.Form.icon] = SepIconConfig.set_url(SepIconConfig.none_file)

        task_code += 1  # 3
        # col_names = ["user_id", "file_url", "user_name", "scm_sep_curr", "scm_sep_new", "when"]
        col_names = ["sep_id", "sep_icon_name", "sep_fullname", "user_curr", "assigned_at", "user_new"]
        grid_const, _ = js_grid_constants(ui_texts["colMetaInfo"], col_names)
        users_sep = []
        item_none = "(None)" if is_str_none_or_empty(ui_texts["itemNone"]) else ui_texts["itemNone"]
        if is_get:
            task_code += 1  # 6
            users_sep, sep_fullname_list, ui_texts[UITextsKeys.Msg.error] = sep_data_fetch(item_none)
        elif request.form.get(js_grid_sec_key) != js_grid_sec_value:
            # TODO: up_handler
            task_code += 2  # 7
            ui_texts[UITextsKeys.Msg.exception] = ui_texts["secKeyViolation"]
            # TODO internal_logout()
        else:
            task_code += 3
            txtGridResponse = request.form.get(js_grid_rsp)
            msg_success, msg_error, task_code = _save_and_email(txtGridResponse, ui_texts, task_code)
            task_code += 1
            _, _, users_sep, sep_fullname_list, msg_error_read = sep_data_fetch(item_none)
            if is_str_none_or_empty(msg_error) and is_str_none_or_empty(msg_error_read):
                ui_texts[UITextsKeys.Msg.success] = msg_success
            elif is_str_none_or_empty(msg_error):
                ui_texts[UITextsKeys.Msg.error] = msg_error_read
            else:
                ui_texts[UITextsKeys.Msg.error] = try_get_mgd_msg(
                    msg_error, ui_texts["saveError"].format(task_code)
                )

        tmpl = render_template(
            template,
            usersSep=users_sep.to_json(),
            sepList=sep_fullname_list,
            **grid_const,
            **ui_texts,
        )

    except Exception as e:
        msg = add_msg_fatal("gridException", ui_texts, task_code)
        _, template, ui_texts = ups_handler(task_code, msg, e, False)
        tmpl = render_template(template, **ui_texts)

    return tmpl


def sep_data_fetch(_item_none) -> Tuple[DBRecords, List[str], str]:

    users_sep, sep_list, msg_error = MgmtSepUser.get_grid_view()
    for record in users_sep.records:
        record.scm_sep_new = _item_none
        record.scm_sep_curr = _item_none if record.scm_sep_curr is None else record.scm_sep_curr
        record.file_url = icon_prepare_for_html(record.sep_id)[0]  # url

    sep_fullname_list = [sep.sep_fullname for sep in sep_list.records]

    return users_sep, sep_fullname_list, msg_error


def _save_and_email(txtGridResponse: str, ui_texts: ui_db_texts, task_code: int) -> sep_mgmt_rtn:
    """Saves data & sends emails"""
    task_code += 1
    jsonGridResponse = json.loads(txtGridResponse)
    task_code += 1
    batch_code = get_batch_code()
    msg_success_save, msg_error, task_code = save_data(jsonGridResponse, batch_code, ui_texts, task_code)
    if not is_str_none_or_empty(msg_error):
        return None, msg_error, task_code

    task_code += 1
    msg_success_email, msg_error, task_code = send_email(batch_code, ui_texts, task_code)
    if not is_str_none_or_empty(msg_error):
        return None, msg_error, task_code

    msg_success = f"{msg_success_save} {msg_success_email}"
    return msg_success, None, task_code


# eof

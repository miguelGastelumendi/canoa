"""
SEP Management and User assignment
    Main module

"""

# cSpell: ignore samp sepsusr usrlist

import json
from flask import render_template, request
from typing import Tuple, List, Dict

from ...models.public import User
from ...models.private import MgmtSepsUser

from ..sep_icon import do_icon_get_url
from ..SepIconMaker import SepIconMaker

from ...public.ups_handler import ups_handler
from ...common.app_error_assistant import ModuleErrorCode, AppStumbled

from ...helpers.py_helper import is_str_none_or_empty, class_to_dict
from ...helpers.user_helper import get_batch_code
from ...helpers.route_helper import get_private_response_data, init_response_vars
from ...helpers.types_helper import ui_db_texts, sep_mgmt_rtn, cargo_list
from ...helpers.js_grid_helper import js_grid_constants, js_grid_sec_key, js_grid_rsp, js_grid_sec_value
from ...helpers.ui_db_texts_helper import add_msg_final, add_msg_error, UITextsKeys
from ...helpers.db_records.DBRecords import DBRecords, ListOfDBRecords


from .save_to_db import save_data
from .send_email import send_email
from .keys_values import CargoKeys, SepMgmtGridCols


def sep_mgmt() -> str:
    task_code = ModuleErrorCode.SEP_MGMT.value
    _, tmpl_ffn, is_get, ui_texts = init_response_vars()

    sep_data: ListOfDBRecords = []
    user_list = []
    msg_error_save_and_email: str = None
    tmpl = ""
    try:
        task_code += 1  # 1
        tmpl_ffn, is_get, ui_texts = get_private_response_data("sepMgmt")

        task_code += 1  # 2
        ui_texts[UITextsKeys.Form.icon_url] = SepIconMaker.get_url(SepIconMaker.none_file)

        task_code += 1  # 3
        # col_names = ["sep_id", "icon_file_name", "user_curr", "sep_fullname", "user", "assigned_at", "visible"]
        col_names: List[str] = list(class_to_dict(SepMgmtGridCols).values())
        grid_const = js_grid_constants(ui_texts["colMetaInfo"], col_names, task_code)

        sep_data = []
        item_none = ui_texts["itemNone"]
        item_none = "(None)" if is_str_none_or_empty(item_none) else item_none
        if is_get:
            task_code += 1  # 4
            sep_data, user_list = _sep_data_fetch(item_none, col_names)
        elif request.form.get(js_grid_sec_key) != js_grid_sec_value:
            task_code += 2  # 5
            msg = add_msg_error("secKeyViolation", ui_texts)
            raise AppStumbled(msg, task_code, True, True)
        else:
            task_code += 3  # 6
            txt_response = request.form.get(js_grid_rsp)
            json_response: Dict[str, str] = json.loads(txt_response)
            msg_success, msg_error_save_and_email, task_code = _save_and_email(
                json_response, ui_texts, task_code
            )
            sep_data, user_list = _sep_data_fetch(item_none, col_names)

            task_code += 1  # ?
            if is_str_none_or_empty(msg_error_save_and_email):
                ui_texts[UITextsKeys.Msg.success] = msg_success
            elif not is_str_none_or_empty(msg_error_save_and_email):
                ui_texts[UITextsKeys.Msg.error] = msg_error_save_and_email

        tmpl = render_template(
            tmpl_ffn,
            sep_data=sep_data.to_list(),
            user_list=user_list,
            cargo_keys=class_to_dict(CargoKeys),
            **grid_const,
            **ui_texts,
        )

    except Exception as e:
        msg = add_msg_final("gridException", ui_texts, task_code)
        _, tmpl_ffn, ui_texts = ups_handler(task_code, msg, e)
        tmpl = render_template(tmpl_ffn, **ui_texts)

    return tmpl


def _sep_data_fetch(_item_none: str, col_names: List[str]) -> Tuple[DBRecords, List[str], str]:

    sep_usr_rows = MgmtSepsUser.get_seps_usr(col_names)
    for record in sep_usr_rows:
        record.user_curr = _item_none if record.user_curr is None else record.user_curr
        record.user_new = record.user_curr
        record.icon_file_name = do_icon_get_url(record.icon_file_name)  # this is file_name

    user_rows = User.get_all_users(User.disabled == False)
    users_list = [user.username for user in user_rows]

    return sep_usr_rows, users_list


def _save_and_email(grid_response: cargo_list, ui_texts: ui_db_texts, task_code: int) -> sep_mgmt_rtn:
    """Saves data & sends emails"""

    task_code += 1
    batch_code = get_batch_code()
    msg_success_save, msg_error, task_code = save_data(grid_response, batch_code, ui_texts, task_code)
    if not is_str_none_or_empty(msg_error):
        return None, msg_error, task_code

    task_code += 1  # 567
    msg_success_email, msg_error, task_code = send_email(batch_code, ui_texts, task_code)
    if not is_str_none_or_empty(msg_error):
        return None, msg_error, task_code

    msg_success = f"{msg_success_save} {msg_success_email}".strip()
    return msg_success, None, task_code


# eof

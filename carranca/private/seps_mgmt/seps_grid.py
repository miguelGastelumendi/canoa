"""
SEP Management and User assignment

NB: SEP is an old acronym for
    "Setor Estratégico de Planejamento" (Strategic Planning Sector)
    so it was kept here until we find a better name.

Equipe da Canoa -- 2024
mgd 2024-10-09, 2025-04-09  v 1.0 One user <-> one SEP
mgd 2025-04-03              v 2.0 One user -> several SEP
mgd 2025-04-09--21                Refactor

The files involved are:
    carranca/private/seps_mgmt/
        seps_grid.py   -- main
        seps_save.py
        seps_email.py
        seps_keys.py
    carranca/templates/private/
        seps_mgmt.html.j2
    carranca/static/js/
        seps_mgmt.js
    carranca/private/
        models.py [MgmtSepUser]

Database objects:
    view:
        vw_mgmt_seps_user
    trigger:
        vw_mgmt_seps_user__upd (instead of update)
    function:
        vw_mgmt_seps_user__on_upd
    table:
        log_user_sep
        sep.mgmt_sep_id
        sep.mgmt_sep_at
        sep.mgmt_batch_code


"""

# cSpell: ignore mgmt tmpl samp

import json
from flask import render_template, request
from typing import Tuple, List, Dict

from ..models import MgmtSepUser
from ..sep_icon import icon_prepare_for_html
from ..SepIconConfig import SepIconConfig

from ...public.ups_handler import ups_handler
from ...common.app_error_assistant import ModuleErrorCode, AppStumbled

from ...helpers.py_helper import is_str_none_or_empty, class_to_dict
from ...helpers.db_helper import DBRecords, ListOfDBRecords
from ...helpers.user_helper import get_batch_code
from ...helpers.route_helper import get_private_form_data, init_form_vars
from ...helpers.types_helper import ui_db_texts, sep_mgmt_rtn, cargo_list
from ...helpers.js_grid_helper import js_grid_constants, js_grid_sec_key, js_grid_rsp, js_grid_sec_value
from ...helpers.ui_db_texts_helper import add_msg_fatal, add_msg_error, UITextsKeys


from .seps_save import save_data
from .seps_email import send_email
from .seps_keys import CargoKeys, MgmtCol

# TODO:
#   - alter [Close] <—> [Cancel] buttons


def sep_mgmt() -> str:
    task_code = ModuleErrorCode.SEP_MGMT.value
    _, template, is_get, ui_texts = init_form_vars()

    sep_data: ListOfDBRecords = []
    user_list = []
    msg_error_save_and_email: str = None
    tmpl = ""
    try:
        task_code += 1  # 1
        template, is_get, ui_texts = get_private_form_data("sepsMgmt")

        task_code += 1  # 2
        ui_texts[UITextsKeys.Form.icon_url] = SepIconConfig.set_url(SepIconConfig.none_file)

        task_code += 1  # 3
        # col_names = ["sep_id", "icon_url", "user_curr", "sep_fullname", user", "assigned_at"]
        col_names: List[str] = list(class_to_dict(MgmtCol).values())
        grid_const, _ = js_grid_constants(ui_texts["colMetaInfo"], col_names)
        if grid_const == None:
            raise AppStumbled(
                f"Invalid MetaInfo columns mapping: `{ui_texts['colMetaInfo']}` <> [{', '.join(col_names)}].",
                task_code,
            )

        sep_data = []
        item_none = ui_texts["itemNone"]
        item_none = "(None)" if is_str_none_or_empty(item_none) else item_none
        if is_get:
            task_code += 1  # 4
            sep_data, user_list, ui_texts[UITextsKeys.Msg.error] = _sep_data_fetch(item_none, col_names)
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
            sep_data, user_list, msg_error_fetch = _sep_data_fetch(item_none, col_names)

            task_code += 1  # ?
            if is_str_none_or_empty(msg_error_save_and_email) and is_str_none_or_empty(msg_error_fetch):
                ui_texts[UITextsKeys.Msg.success] = msg_success
            elif not is_str_none_or_empty(msg_error_save_and_email):
                ui_texts[UITextsKeys.Msg.error] = msg_error_save_and_email
            else:  # couldn't ready data.
                ui_texts[UITextsKeys.Msg.error] = msg_error_fetch

        tmpl = render_template(
            template,
            sep_data=sep_data.to_json(),
            user_list=user_list,
            cargo_keys=class_to_dict(CargoKeys),
            **grid_const,
            **ui_texts,
        )

    except Exception as e:
        msg = add_msg_fatal("gridException", ui_texts, task_code)
        _, template, ui_texts = ups_handler(task_code, msg, e)
        tmpl = render_template(template, **ui_texts)

    return tmpl


def _sep_data_fetch(_item_none: str, col_names: List[str]) -> Tuple[DBRecords, List[str], str]:

    sep_data, user_data, msg_error = MgmtSepUser.get_grid_view(col_names)
    for record in sep_data.records:
        record.user_curr = _item_none if record.user_curr is None else record.user_curr
        record.user_new = record.user_curr
        record.icon_url = icon_prepare_for_html(record.sep_id)[0]  # url

    users_list = [user.username for user in user_data.records]

    return sep_data, users_list, msg_error


def _save_and_email(grid_response: cargo_list, ui_texts: ui_db_texts, task_code: int) -> sep_mgmt_rtn:
    """Saves data & sends emails"""

    task_code += 1
    batch_code = get_batch_code()
    msg_success_save, msg_error, task_code = save_data(grid_response, batch_code, ui_texts, task_code)
    if not is_str_none_or_empty(msg_error):
        return None, msg_error, task_code

    task_code += 1
    msg_success_email, msg_error, task_code = send_email(batch_code, ui_texts, task_code)
    if not is_str_none_or_empty(msg_error):
        return None, msg_error, task_code

    msg_success = f"{msg_success_save} {msg_success_email}".strip()
    return msg_success, None, task_code


# eof

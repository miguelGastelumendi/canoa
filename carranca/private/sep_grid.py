"""
SEP
Grid form Adm

mgd
"""

# cSpell: ignore samp sepsusr usrlist

from typing import Tuple, List

from .sep_icon import do_icon_get_url
from .SepIconMaker import SepIconMaker
from ..models.private import MgmtSepsUser
from ..public.ups_handler import ups_handler
from ..common.app_error_assistant import ModuleErrorCode, AppStumbled

from ..helpers.py_helper import class_to_dict
from ..helpers.uiact_helper import UiActResponseKeys
from ..helpers.jinja_helper import jinja_template, process_template
from ..helpers.route_helper import get_private_response_data, init_response_vars
from ..helpers.js_consts_helper import js_grid_col_meta_info,  js_ui_dictionary
from ..helpers.ui_db_texts_helper import add_msg_final, UITextsKeys
from ..helpers.db_records.DBRecords import DBRecords, ListOfDBRecords


def get_sep_grid() -> jinja_template:
    task_code = ModuleErrorCode.SEP_GRID.value
    _, tmpl_rfn, is_get, ui_texts = init_response_vars()

    sep_data: ListOfDBRecords = []
    tmpl = ""
    try:
        task_code += 1  # 1
        tmpl_rfn, is_get, ui_texts = get_private_response_data("sepGrid")

        task_code += 1  # 2
        ui_texts[UITextsKeys.Form.icon_url] = SepIconMaker.get_url(
            SepIconMaker.empty_file
        )

        task_code += 1  # 3
        col_names = ["id", "icon_file_name", "scm_name", "name", "user_curr", "visible"]
        js_ui_dict = js_ui_dictionary(ui_texts[js_grid_col_meta_info], col_names, task_code)

        sep_data = []
        if is_get:
            task_code += 1  # 4
            sep_data = _sep_data_fetch(col_names)
        else:
            raise AppStumbled("Unexpected route method.")

        task_code += 2  # 5/6
        tmpl = process_template(
            tmpl_rfn,
            sep_data=sep_data.to_list(),
            cargo_keys=class_to_dict(UiActResponseKeys),
            **ui_texts,
            **js_ui_dict,
            )

    except AppStumbled as e:
        _, tmpl_rfn, ui_texts = ups_handler(task_code, '',  e)
        tmpl = process_template(tmpl_rfn, **ui_texts)

    except Exception as e:
        msg = add_msg_final("gridException", ui_texts, task_code)
        _, tmpl_rfn, ui_texts = ups_handler(task_code, msg, e)
        tmpl = process_template(tmpl_rfn, **ui_texts)

    return tmpl


def _sep_data_fetch(col_names: List[str]) -> Tuple[DBRecords]:
    sep_usr_rows = MgmtSepsUser.get_seps_usr(col_names)
    for record in sep_usr_rows:
        sep_id = record.id
        record.id = MgmtSepsUser.code(sep_id)
        record.icon_file_name = do_icon_get_url(record.icon_file_name, sep_id)

    return sep_usr_rows


# eof

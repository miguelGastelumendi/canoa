"""
SEP
    Grid form Adm
"""

# cSpell: ignore tmpl samp sepsusr usrlist

import json
from flask import render_template, request
from typing import Tuple, List, Dict

from ..helpers.js_grid_helper import js_grid_constants

from .sep_icon import do_icon_get_url

from ..private.SepIconConfig import SepIconConfig

from ..models.private import MgmtSepsUser

from ..public.ups_handler import ups_handler
from ..common.app_error_assistant import ModuleErrorCode, AppStumbled

from ..helpers.route_helper import get_private_response_data, init_response_vars
from ..helpers.ui_db_texts_helper import add_msg_fatal, UITextsKeys
from ..helpers.db_records.DBRecords import DBRecords, ListOfDBRecords


def sep_crud() -> str:
    task_code = ModuleErrorCode.SEP_CRUD.value
    _, tmpl_ffn, is_get, ui_texts = init_response_vars()

    sep_data: ListOfDBRecords = []
    tmpl = ""
    try:
        task_code += 1  # 1
        tmpl_ffn, is_get, ui_texts = get_private_response_data("sepCrud")

        task_code += 1  # 2
        ui_texts[UITextsKeys.Form.icon_url] = SepIconConfig.get_icon_url(SepIconConfig.none_file)

        task_code += 1  # 3
        col_names = ["id", "icon_file_name", "scm_name", "name", "user_curr"]
        grid_const = js_grid_constants(ui_texts["colMetaInfo"], col_names, task_code)

        sep_data = []
        if is_get:
            task_code += 1  # 4
            sep_data = _sep_data_fetch(col_names)
        else:
            raise AppStumbled("Unexpected route method.")

        tmpl = render_template(
            tmpl_ffn,
            sep_data=sep_data.to_list(),
            **grid_const,
            **ui_texts,
        )

    except Exception as e:
        msg = add_msg_fatal("gridException", ui_texts, task_code)
        _, tmpl_ffn, ui_texts = ups_handler(task_code, msg, e)
        tmpl = render_template(tmpl_ffn, **ui_texts)

    return tmpl


def _sep_data_fetch(col_names: List[str]) -> Tuple[DBRecords]:

    sep_usr_rows = MgmtSepsUser.get_seps_usr(col_names)
    for record in sep_usr_rows:
        record.icon_file_name = do_icon_get_url(record.icon_file_name)  # this is file_name

    return sep_usr_rows


# eof

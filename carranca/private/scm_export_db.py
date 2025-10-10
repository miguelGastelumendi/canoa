"""
Create/Udpate Schema & SEP on the Database

mgd 2025.10
"""

import json

from .sep_icon import do_icon_get_url
from .scm_data import SchemaData, get_scm_data
from ..helpers.uiact_helper import UiActCmdKeys
from ..helpers.py_helper import class_to_dict
from ..public.ups_handler import ups_handler
from ..helpers.types_helper import jinja_template
from ..helpers.jinja_helper import process_template
from ..helpers.route_helper import get_private_response_data, init_response_vars, template_file_full_name
from ..helpers.js_consts_helper import js_grid_col_meta_info, js_ui_dictionary
from ..helpers.ui_db_texts_helper import add_msg_final
from ..config.ExportProcessConfig import ExportProcessConfig
from ..common.app_error_assistant import ModuleErrorCode
from ..models.private_1.ExportGrid import ExportGrid



def scm_export_db() -> jinja_template:

    task_code = ModuleErrorCode.SCM_EXPORT
    _, tmpl_rfn, is_get, ui_texts = init_response_vars()

    tmpl = ""
    try:
        task_code += 1
        tmpl_rfn, is_get, ui_texts = get_private_response_data("scmExportDB")


        task_code += 1
        tmpl: jinja_template = process_template(
            tmpl_rfn,
            **ui_texts,
        )
    except Exception as e:
        msg = add_msg_final("scmExportDBException", ui_texts, task_code)
        _, tmpl_rfn, ui_texts = ups_handler(task_code, msg, e)
        tmpl = process_template(tmpl_rfn, **ui_texts)

    return tmpl

#eof
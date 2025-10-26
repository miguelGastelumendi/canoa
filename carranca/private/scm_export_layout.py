"""
scm_export_layout

Saves the Schema & SEP User Interface layout

mgd 2025.08
"""
from .sep_icon import do_icon_get_url
from .scm_data import scm_data_get
from ..helpers.py_helper import class_to_dict
from ..public.ups_handler import ups_handler
from ..helpers.uiact_helper import UiActResponseKeys, UiActResponse
from ..helpers.types_helper import jinja_template
from ..helpers.jinja_helper import process_template
from ..helpers.route_helper import get_private_response_data, init_response_vars, template_file_full_name
from ..helpers.js_consts_helper import js_grid_col_meta_info, js_ui_dictionary
from ..helpers.ui_db_texts_helper import add_msg_error, add_msg_success, add_msg_final
from ..common.app_error_assistant import ModuleErrorCode
from ..models.private_1.ExportGrid import ExportGrid


def scm_export_layout(uiact_rsp: UiActResponse) -> jinja_template:

    task_code = ModuleErrorCode.SCM_LAYOUT

    _, tmpl_rfn, is_get, ui_texts = init_response_vars()

    tmpl = ""
    try:
        task_code += 1
        tmpl_rfn, is_get, ui_texts = get_private_response_data("scmLayout")

        task_code += 1

        # if success:
        add_msg_success("layoutSuccess", ui_texts)

        # if error:
        add_msg_error("layoutError", ui_texts, "'Nome de esquema repetido.'",  task_code)

        task_code += 1
        tmpl: jinja_template = process_template(
            tmpl_rfn,
            cargo_keys=class_to_dict(UiActResponseKeys),
            **ui_texts,
        )
    except Exception as e:
        msg = add_msg_final("layoutExcept", ui_texts, task_code)
        _, tmpl_rfn, ui_texts = ups_handler(task_code, msg, e)
        tmpl = process_template(tmpl_rfn, **ui_texts)

    return tmpl

#eof
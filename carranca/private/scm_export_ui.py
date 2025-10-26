"""
Schema & Seps

A json containing the Schema table and its visible SEP is generated
to organize the information to submit to the DB.

mgd 2025.08
"""
from .sep_icon import do_icon_get_url
from .scm_data import scm_data_get
from ..helpers.py_helper import class_to_dict
from ..public.ups_handler import ups_handler
from ..helpers.types_helper import jinja_template
from ..helpers.jinja_helper import process_template
from ..helpers.uiact_helper import UiActResponse, UiActResponseKeys
from ..helpers.route_helper import get_private_response_data, init_response_vars, template_file_full_name
from ..helpers.js_consts_helper import js_grid_col_meta_info, js_ui_dictionary
from ..helpers.ui_db_texts_helper import add_msg_final
from ..config.ExportProcessConfig import ExportProcessConfig
from ..common.app_error_assistant import ModuleErrorCode
from ..models.private_1.ExportGrid import ExportGrid


def scm_export_ui(uiact_rsp: UiActResponse) -> jinja_template:

    task_code = ModuleErrorCode.SCM_EXPORT_UI
    _, tmpl_rfn, _, ui_texts = init_response_vars()

    scm_cols = ["name", "color"]
    sep_cols = ["name", "icon_file_name", "mgmt_users_id", "ui_order" ]

    tmpl = ""
    try:
        task_code += 1
        tmpl_rfn, _, ui_texts = get_private_response_data("scmExportUI")

        task_code += 1
        config = ExportProcessConfig(scm_cols, sep_cols)
        task_code += 1
        schema_data, coder, task_code = scm_data_get(task_code, False, config)
        task_code += 1
        grid_data = ExportGrid.get_data()
        task_code += 1
        empty_icon = do_icon_get_url("")

        task_code += 1
        col_names = ["id", "sep_id", "scm_id", "file_name", "sep_fullname", "uploaded", "report_errors"]
        js_ui_dict = js_ui_dictionary(ui_texts[js_grid_col_meta_info], col_names, task_code)

        task_code += 1
        tmpl: template_file_full_name = process_template(
            tmpl_rfn,
            schemas=schema_data.schemas,
            grid_data = grid_data.to_list(),
            empty_icon= empty_icon,
            cargo_keys=class_to_dict(UiActResponseKeys),
            cargo_data= uiact_rsp.initial(),
            **ui_texts,
            **js_ui_dict,
        )
    except Exception as e:
        msg = add_msg_final("scmExportException", ui_texts, task_code)
        _, tmpl_rfn, ui_texts = ups_handler(task_code, msg, e)
        tmpl = process_template(tmpl_rfn, **ui_texts)

    return tmpl

#eof
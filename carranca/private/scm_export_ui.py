"""
Schema & Seps

A json containing the Schema table and its visible SEP is generated
to organize the informaction to submit to the DB.

mgd 2025.08
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


def test_scm_data() -> SchemaData:
    config = ExportProcessConfig()
    task_code = ModuleErrorCode.SCM_EXPORT
    scm_data = get_scm_data( task_code, True, config.scm_cols, config.sep_cols )
    scm_data.header = config.header

    task_code += 1
    # Convert the final dictionary to a JSON string
    if False:
        jsn_data = json.dumps(scm_data, **config.json)
        from .scm_import import do_scm_import

        dic_data = do_scm_import(jsn_data)
        print(dic_data)

    return scm_data


def scm_export_ui() -> jinja_template:

    task_code = ModuleErrorCode.SCM_EXPORT
    _, tmpl_rfn, is_get, ui_texts = init_response_vars()

    scm_cols = ["name", "color"]
    sep_cols = ["name", "icon_file_name", "mgmt_users_id", "ui_order" ]

    tmpl = ""
    try:
        task_code += 1
        tmpl_rfn, is_get, ui_texts = get_private_response_data("scmExportUI")

        task_code += 1
        schema_data = get_scm_data(task_code, False, scm_cols, sep_cols)
        schema_data.header = ExportProcessConfig().header

        grid_data = ExportGrid.get_data()
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
            cargo_keys=class_to_dict(UiActCmdKeys),
            **ui_texts,
            **js_ui_dict,
        )
    except Exception as e:
        msg = add_msg_final("scmExportException", ui_texts, task_code)
        _, tmpl_rfn, ui_texts = ups_handler(task_code, msg, e)
        tmpl = process_template(tmpl_rfn, **ui_texts)

    return tmpl

#eof
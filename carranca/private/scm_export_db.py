"""
Create/Update Schema & SEP on the Database

mgd 2025.10
"""

import json

from .scm_data import scm_data_get
from ..helpers.py_helper import class_to_dict
from ..public.ups_handler import ups_handler
from ..helpers.types_helper import JinjaTemplate
from ..helpers.jinja_helper import process_template
from ..helpers.uiact_helper import UiActResponse, UiActResponseKeys
from ..helpers.route_helper import get_private_response_data, init_response_vars
from ..helpers.ui_db_texts_helper import add_msg_error, add_msg_success, add_msg_final
from ..config.ExportProcessConfig import ExportProcessConfig
from ..common.app_error_assistant import ModuleErrorCode


def scm_export_db(uiact_rsp: UiActResponse) -> JinjaTemplate:

    task_code = ModuleErrorCode.SCM_EXPORT_DB
    _, tmpl_rfn, is_get, ui_texts = init_response_vars()

    tmpl = ""
    try:
        task_code += 1
        tmpl_rfn, is_get, ui_texts = get_private_response_data("scmExportDB")

        task_code += 1
        config = ExportProcessConfig()
        task_code += 1
        schema_data, coder, task_code = scm_data_get(task_code, True, config)

        task_code += 1
        if False:
            # Convert the final dictionary to a JSON string
            data = class_to_dict(schema_data)
            jsn_data = json.dumps(data, **config.json)
            from .scm_import import do_scm_import
            # recover coder n case is needed
            schema_data.coder = coder

            dic_data = do_scm_import(jsn_data)
            # Convert to SQL statements
            print(dic_data)


        # if success:
        add_msg_success("exportSuccess", ui_texts)

        # if error:
        add_msg_error("exportError", ui_texts, "'Nome de esquema repetido.'",  task_code)

        task_code += 1
        tmpl: JinjaTemplate = process_template( tmpl_rfn, **ui_texts )
    except Exception as e:
        msg = add_msg_final("exportException", ui_texts, task_code)
        _, tmpl_rfn, ui_texts = ups_handler(task_code, msg, e)
        tmpl = process_template(tmpl_rfn, **ui_texts)

    return tmpl

#eof
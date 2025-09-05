"""
Schema
Schema & Seps data export

A json containing the Schema table and its visible SEP is generated.

mgd 2025.08
"""

import json
from typing import Dict, List

from ..public.ups_handler import ups_handler
from ..config.ExportProcessConfig import ExportProcessConfig, UsualDict
from ..common.app_error_assistant import ModuleErrorCode
from ..models.private_1.SchemaGrid import SchemaGrid
from ..models.private import Sep

from ..helpers.jinja_helper import process_template
from ..helpers.route_helper import get_private_response_data, init_response_vars
from ..helpers.ui_db_texts_helper import add_msg_final


def do_scm_export( ) -> str:
    test_jsn= True

    task_code = ModuleErrorCode.SCM_EXPORT
    _, tmpl_ffn, is_get, ui_texts = init_response_vars()

    tmpl = ""
    try:
        task_code += 1
        tmpl_ffn, is_get, ui_texts = get_private_response_data("scmExport")

        if False:
             do_scm_export(test_jsn)

        tmpl = process_template(
            tmpl_ffn,
            **ui_texts
        )
    except Exception as e:
        msg = add_msg_final("exportException", ui_texts, task_code)
        _, tmpl_ffn, ui_texts = ups_handler(task_code, msg, e)
        tmpl = process_template(tmpl_ffn, **ui_texts)

    return tmpl


def get_scm_export( task_code: int, test_jsn: bool = False ) -> UsualDict:
        SEPS_KEY = "seps"
        scm_id = SchemaGrid.id.name
        config = ExportProcessConfig()
        task_code += 1

        # file_fullname = config.full_file_name
        scm_cols = config.scm_cols
        task_code += 1
        if scm_id not in scm_cols:
            #  Scheme's PK is needed in order to get seps by FK
            scm_cols.insert(0, scm_id)

        task_code += 1
        scm_rows = SchemaGrid.get_schemas(scm_cols, True)
        schema_list: List[Dict] = []
        sep_rows: List[Sep] = []
        task_code += 1
        for scm in scm_rows:
            schema_dic = scm.encode64([scm_id])
            schema_dic[SEPS_KEY]: List[Sep] = []
            sep_rows = Sep.get_visible_seps_of_schema(scm.id, config.sep_cols)
            for sep in sep_rows:
                schema_dic[SEPS_KEY].append(sep.encode64())

            schema_list.append(schema_dic)
        task_code += 1
        meta_scm = scm_rows.col_info
        schema_data = {
            "header": config.header,
            "meta_scm": meta_scm,
            "meta_sep": (sep_rows.col_info if sep_rows else []),
            "schemas": schema_list,
        }

        task_code += 1
        # Convert the final dictionary to a JSON string
        if test_jsn:
            jsn_data = json.dumps(schema_data, **config.json)
            from .scm_import import do_scm_import

            dic_data = do_scm_import(jsn_data)
            print(dic_data)

        return schema_data

#eof
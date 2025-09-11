"""
Schema
Schema & Seps data export

A json containing the Schema table and its visible SEP is generated.

mgd 2025.08
"""

import json
from typing import Dict, List


from .sep_icon import do_icon_get_url
from .grid_helper import GridCargoKeys
from ..models.public import User
from ..models.private import Sep
from ..helpers.py_helper import class_to_dict
from ..public.ups_handler import ups_handler
from ..helpers.jinja_helper import process_template
from ..helpers.route_helper import get_private_response_data, init_response_vars, template_file_full_name
from ..helpers.js_grid_helper import js_grid_col_meta_info,  js_grid_constants
from ..helpers.ui_db_texts_helper import add_msg_final
from ..config.ExportProcessConfig import ExportProcessConfig, UsualDict
from ..common.app_error_assistant import ModuleErrorCode
from ..models.private_1.SchemaGrid import SchemaGrid
from ..models.private_1.ExportGrid import ExportGrid


class SchemaData:
    header: UsualDict
    meta_scm: UsualDict
    meta_sep: UsualDict
    schemas: List[UsualDict]

    def __init__(self, header: UsualDict, meta_scm: UsualDict,    meta_sep: UsualDict,    schemas: List[UsualDict]):
        self.header = header
        self.meta_scm = meta_scm
        self.meta_sep = meta_sep
        self.schemas = schemas


def get_scm_export( ) -> str:

    task_code = ModuleErrorCode.SCM_EXPORT
    _, tmpl_ffn, is_get, ui_texts = init_response_vars()

    scm_cols = ["name", "color"]
    # mgmt_users_id == sep.users_id
    sep_cols = ["name", "icon_file_name", "mgmt_users_id", "ui_order" ]


    tmpl = ""
    try:
        task_code += 1
        tmpl_ffn, is_get, ui_texts = get_private_response_data("scmExport")

        task_code += 1
        schema_data = _get_scm_data(task_code, False, scm_cols, sep_cols)
        grid_data = ExportGrid.get_data()
        empty_icon = do_icon_get_url("")

        task_code += 1
        col_names = ["id", "sep_id", "scm_id", "file_name", "sep_fullname", "uploaded", "report_errors"]
        grid_const = js_grid_constants(ui_texts[js_grid_col_meta_info], col_names, task_code)

        task_code += 1
        tmpl: template_file_full_name = process_template(
            tmpl_ffn,
            schemas=schema_data.schemas,
            grid_data = grid_data.to_list(),
            empty_icon= empty_icon,
            cargo_keys=class_to_dict(GridCargoKeys),
            **ui_texts,
            **grid_const,
        )
    except Exception as e:
        msg = add_msg_final("scmExportException", ui_texts, task_code)
        _, tmpl_ffn, ui_texts = ups_handler(task_code, msg, e)
        tmpl = process_template(tmpl_ffn, **ui_texts)

    return tmpl


def get_scm_data( ) -> SchemaData:
    config = ExportProcessConfig()
    task_code = ModuleErrorCode.SCM_EXPORT
    scm_data = _get_scm_data( task_code, True, config.scm_cols, config.sep_cols )
    scm_data.header = config.header

    task_code += 1
    # Convert the final dictionary to a JSON string
    if False:
        jsn_data = json.dumps(scm_data, **config.json)
        from .scm_import import do_scm_import

        dic_data = do_scm_import(jsn_data)
        print(dic_data)

    return scm_data


def _get_scm_data( task_code: int, encode64:bool, scm_cols: List[str], sep_cols: List[str] ) -> SchemaData:
        SEPS_KEY = "seps"
        scm_id = SchemaGrid.id.name
        sep_id = Sep.id.name

        task_code += 1

        # check if need PK => FK where selected
        task_code += 1
        if scm_id not in scm_cols:
            scm_cols.insert(0, scm_id)

        task_code += 1
        if sep_id not in sep_cols:
            sep_cols.append(sep_id)

        task_code += 1
        scm_rows = SchemaGrid.get_schemas(scm_cols, True)
        schema_list: List[Dict] = []
        sep_rows: List[Sep] = []
        mng_list: Dict = {}

        if Sep.users_id.name in sep_cols:
            user_rows = User.get_all_users(User.disabled == False, User.id)
            mng_list =  {user.id: user.username for user in user_rows}


        get_icon= Sep.icon_file_name.name in sep_cols
        task_code += 1
        mgmt: str = None
        for scm in scm_rows:
            schema_dic = scm.encode64([scm_id]) if encode64 else scm.copy([scm_id])
            schema_dic[SEPS_KEY]: List[Sep] = []
            sep_rows = Sep.get_visible_seps_of_scm(scm.id, sep_cols)
            for sep in sep_rows:
                sep.icon_file_name = do_icon_get_url(sep.icon_file_name, sep.id)  if get_icon else None
                sep.manager = mgmt if mng_list and (mgmt:= mng_list.get(sep.mgmt_users_id)) else "?"
                schema_dic[SEPS_KEY].append(sep.encode64([sep_id]) if encode64 else sep.copy([sep_id]))

            schema_list.append(schema_dic)

        task_code += 1
        meta_scm = scm_rows.col_info
        meta_sep = sep_rows.col_info if sep_rows else []
        schema_data = SchemaData(None, meta_scm, meta_sep, schema_list)

        return schema_data

#eof
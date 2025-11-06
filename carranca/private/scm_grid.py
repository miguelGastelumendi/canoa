"""
Schema
Grid form Adm

mgd
"""

# cSpell: ignore samp sepsusr usrlist

from typing import List

from ..public.ups_handler import ups_handler
from ..common.app_error_assistant import ModuleErrorCode, AppStumbled
from ..models.private_1.SchemaGrid import SchemaGrid

from ..helpers.py_helper import class_to_dict
from ..helpers.uiact_helper import UiActResponseKeys
from ..helpers.jinja_helper import process_template
from ..helpers.types_helper import JinjaTemplate
from ..helpers.route_helper import get_private_response_data, init_response_vars
from ..helpers.js_consts_helper import js_grid_col_meta_info,  js_ui_dictionary
from ..helpers.ui_db_texts_helper import add_msg_final
from ..helpers.db_records.DBRecords import DBRecords, ListOfDBRecords


def get_scm_grid() -> JinjaTemplate:

    def _scm_data_fetch(col_names: List[str]) -> DBRecords:
        scm_rows = SchemaGrid.get_schemas(col_names)
        for record in scm_rows:
            scm_id = record.id
            record.id = SchemaGrid.code(scm_id)
        return scm_rows

    task_code = ModuleErrorCode.SCM_GRID.value
    _, tmpl_rfn, is_get, ui_texts = init_response_vars()

    scm_data: ListOfDBRecords = []
    tmpl = ""
    try:
        task_code += 1  # 1
        tmpl_rfn, is_get, ui_texts = get_private_response_data("scmGrid")

        task_code += 1  # 2
        col_names = ["id", "name", "color", "visible", "sep_v2t"]
        js_ui_dict = js_ui_dictionary(ui_texts[js_grid_col_meta_info], col_names, task_code)

        scm_data = []
        if is_get:
            task_code += 1  # 3
            scm_data = _scm_data_fetch(col_names)
        else:
            raise AppStumbled("Unexpected route method.")

        tmpl = process_template(
            tmpl_rfn,
            scm_data=scm_data.to_list(),
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


# eof

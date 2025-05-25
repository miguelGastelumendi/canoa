"""
Grid HTML + js + py communication constants

Equipe da Canoa -- 2025
mgd 2025-01-19
"""

# cSpell:ignore

import json
from typing import Tuple, List

from ..common.app_error_assistant import AppStumbled
from .types_helper import ui_db_texts


# === Global constants Keys for grid_const Jinja Dictionary for j2 grid ====
#
#  Key name const
#  --------------
#  Uses Python variable style names and starts with 'js_grid'
#
#  grid_const Key name
#  -------------------
#  Uses Python variable style names and starts with 'grid_'
#
#  uiTexts Key name
#  ----------------
#  Uses PascalCase style names (see ui_items Database View)

#  Key name const
js_grid_sec_key = "grid_sec_key"
js_grid_rsp = "grid_rsp"
js_grid_submit_id = "grid-submit-id"

# TODO: create a real key with user_id and datetime
js_grid_sec_value = "7298kaj0fk9dl-sd=)0y"


def js_grid_constants(col_meta_info_txt: str, col_names: List[str], task_code: int) -> ui_db_texts:

    task_code = 1
    grid_const: ui_db_texts = {}

    col_meta_info_json = json.loads(col_meta_info_txt)
    col_meta_info_array = [{"n": key, "h": col_meta_info_json[key]} for key in col_meta_info_json]
    col_meta_info_names = {item["n"] for item in col_meta_info_array}

    if col_meta_info_names and not set(col_names).issubset(col_meta_info_names):
        missing_keys = set(col_names) - col_meta_info_names
        # this is an for the developer
        raise AppStumbled(
            f"Invalid MetaInfo columns mapping: `{col_meta_info_txt}` <> [{', '.join(col_names)}]. Missing keys: {missing_keys}",
            task_code,
        )

    grid_const["grid_id"] = "gridID"
    grid_const[js_grid_rsp] = js_grid_rsp  # grid Response
    grid_const[js_grid_submit_id] = js_grid_submit_id  # id of the submit button/form
    grid_const[js_grid_sec_key] = js_grid_sec_key  # security token key
    grid_const["grid_sec_value"] = js_grid_sec_value  # security token value
    # short for 'n': name, 'h': header
    grid_const["grid_col_meta"] = [{"n": key, "h": col_meta_info_json[key]} for key in col_meta_info_json]

    return grid_const


# eof

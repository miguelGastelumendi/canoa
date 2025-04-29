"""
Grid HTML + js + py communication constants

Equipe da Canoa -- 2025
mgd 2025-01-19
"""

# cSpell:ignore

import json
from typing import Tuple, List
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


def js_grid_constants(col_mi_txt: str, col_names: List[str]) -> Tuple[ui_db_texts, int]:

    task_code = 1
    grid_const: ui_db_texts = {}

    col_mi = json.loads(col_mi_txt)
    col_meta_info = [{"n": key, "h": col_mi[key]} for key in col_mi]
    col_mi_names = {item["n"] for item in col_meta_info}

    if col_mi_names and not set(col_names).issubset(col_mi_names):
        missing_keys = set(col_names) - col_mi_names
        print(f"Missing keys: {missing_keys}")  # TODO
        return None, 8

    grid_const["grid_id"] = "gridID"

    grid_const[js_grid_rsp] = js_grid_rsp  # grid Response
    grid_const[js_grid_submit_id] = js_grid_submit_id  # id of the submit button/form
    grid_const[js_grid_sec_key] = js_grid_sec_key  # security token key
    grid_const["grid_sec_value"] = js_grid_sec_value  # security token value
    grid_const["grid_col_meta"] = [{"n": key, "h": col_mi[key]} for key in col_mi]

    return grid_const, task_code


# eof

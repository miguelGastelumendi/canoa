"""
    Grid HTML + js + py communication constants

    Equipe da Canoa -- 2025
    mgd 2025-01-19
"""

import json
from typing import Tuple, List
from .hints_helper import UI_Texts


# === Global constants Keys for grid_const Jinja Dictionary for j2 grid ======================
#
#  Key name const
#  --------------
#  Uses Python variable style names and starts with 'ui_grid'
#
#  grid_const Key name
#  ---------
#  Uses Python variable style names and starts with 'grid_'
#
#  uiTexts Key name
#  ----------------
#  Uses PascalCase style names (see ui_items Database View)

#  Key name const
ui_grid_sec_key = "grid_sec_key"
ui_grid_rsp = "grid_rsp"
ui_grid_submit_id = "grid_submit_id"

# TODO: create a real key with user_id and datetime
js_grid_sec_value = "7298kaj0fk9dl-sd=)0y"


def grid_Constants(col_mi_txt: str, col_names: List[str]) -> Tuple[UI_Texts, int]:

    task_code = 1
    grid_const: UI_Texts = {}

    col_mi = json.loads(col_mi_txt)
    col_meta_info = [{"n": key, "h": col_mi[key]} for key in col_mi]
    col_mi_names = {item["n"] for item in col_meta_info}

    if col_mi_names and not set(col_names).issubset(col_mi_names):
        missing_keys = set(col_names) - col_mi_names
        print(f"Missing keys: {missing_keys}")
        return None, 8

    grid_const["grid_id"] = "gridID"

    grid_const[ui_grid_rsp] = ui_grid_rsp  # grid Response
    grid_const[ui_grid_submit_id] = ui_grid_submit_id  # id of the submit button/form
    grid_const[ui_grid_sec_key] = ui_grid_sec_key  # security token key
    grid_const["grid_sec_value"] = js_grid_sec_value  # security token value
    grid_const["grid_col_meta"] = [{"n": key, "h": col_mi[key]} for key in col_mi]

    return grid_const, task_code


# eof

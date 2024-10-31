"""
    User Profile's Management and SEP assignment

    Equipe da Canoa -- 2024
    mgd 2024-10-09
"""

# cSpell: ignore mgmt tmpl

import json
from typing import Tuple
from flask import render_template, request

from .models import MgmtUser
from ..helpers.route_helper import get_private_form_data


def do_profile_mgmt() -> str:
    template, is_get, texts = get_private_form_data("profileMgmt")
    js_grid_sec_value = "7298kaj0fk9dl-sd=)0"
    js_grid_sec_key = "gridSecKey"
    js_grid_rsp = "gridRsp"

    if is_get:
        # Até criar ui_texts:
        texts["itemNone"] = "(nenhum)"
        texts["itemRemove"] = "(remover)"
        # py/js communication
        texts[js_grid_rsp] = js_grid_rsp
        texts["gridSecValue"] = js_grid_sec_value
        texts[js_grid_sec_key] = js_grid_sec_key

        users_sep, sep_list, msg_error = MgmtUser.get_grid_view(texts["itemNone"])

        sep_name_list = [sep["name"] for sep in sep_list]
        tmpl = render_template(template, usersSep=users_sep, sepList=sep_name_list, **texts)
    elif request.form.get(js_grid_sec_key) != js_grid_sec_value:
        # TODO: error
        pass
    else:
        gridResponse = request.form.get(js_grid_rsp)
        grid_response = json.loads(gridResponse)
        msg_success, msg_error = _apply_data(grid_response)
        print(grid_response)

    return tmpl


def _apply_data(grid_response: dict) -> Tuple[str, str]:

    task_code = 1
    msg_success = "Ok"
    msg_error = ""
    try:
        actions = grid_response["actions"]
        task_code += 1
        str_remove = actions["remove"]
        task_code += 1
        str_none = actions["none"]
        task_code += 1
        remove = []
        assign = []
        problem = []
        none = 0
        grid = grid_response["grid"]
        seps = [item["sep_name"] for item in grid]
        task_code += 1
        for item in grid:
            sep_new = item["sep_new"]
            if sep_new == str_none:
                none += 1
            elif sep_new != str_remove:  # new sep
                assign.append(item)
            elif item["sep_name"] != str_none:  # ignore remove none
                remove.append(item)

        msg_error = MgmtUser.save_grid_view(remove, assign)
    except Exception as e:
        msg_error = str(e)

    return msg_success, msg_error

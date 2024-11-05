"""
    User Profile's Management and SEP assignment

    Equipe da Canoa -- 2024
    mgd 2024-10-09
"""

# cSpell: ignore mgmt tmpl

import json
from typing import Tuple
from flask import render_template, request

from ..helpers.Display import is_str_none_or_empty

from .models import MgmtSepUser
from ..helpers.route_helper import get_private_form_data


def do_sep_mgmt() -> str:
    template, is_get, texts = get_private_form_data("sepMgmt")
    js_grid_sec_value = "7298kaj0fk9dl-sd=)0x"
    js_grid_sec_key = "gridSecKey"
    js_grid_rsp = "gridRsp"
    js_grid_submit_id = "gridSubmitID"

    # Até criar ui_texts:
    texts["itemNone"] = "(nenhum)"
    texts["itemRemove"] = "(remover)"
    # py/js communication
    texts[js_grid_rsp] = js_grid_rsp
    texts["gridSecValue"] = js_grid_sec_value
    texts[js_grid_submit_id] = js_grid_submit_id
    texts[js_grid_sec_key] = js_grid_sec_key

    def _get_grid_data():
        users_sep, sep_list, msg_error = MgmtSepUser.get_grid_view(texts["itemNone"])
        sep_name_list = [sep["name"] for sep in sep_list]
        return users_sep, sep_name_list, msg_error

    if is_get:
        users_sep, sep_name_list, msg_error = _get_grid_data()
        texts["msgInfo"] = (
            """
            Para atribuir um SEP, selecione um da lista 'Novo SEP'.
            Use o item (Remover) para cancelar a atribuição.
            Para criar um novo SEP, use o botão [Adicionar] e [Editar] para alterá-lo.
            """
        )
    elif request.form.get(js_grid_sec_key) != js_grid_sec_value:
        texts["msgError"] = "A chave mudou."
        # TODO goto login
    else:
        txtGridResponse = request.form.get(js_grid_rsp)
        jsonGridResponse = json.loads(txtGridResponse)
        msg_success, msg_error_save = _apply_data(jsonGridResponse)
        users_sep, sep_name_list, msg_error_read = _get_grid_data()
        if is_str_none_or_empty(msg_error_save) and is_str_none_or_empty(msg_error_read):
            texts["msgSuccess"] = "As mudanças foram salvas."
        elif is_str_none_or_empty(msg_error_save):
            texts["msgError"] = msg_error_save
        else:
            texts["msgError"] = msg_error_read

        # TODO show final, with email sent

    tmpl = render_template(template, usersSep=users_sep, sepList=sep_name_list, **texts)
    return tmpl


def _apply_data(grid_response: dict) -> Tuple[str, str]:

    task_code = 1
    msg_success = "As modificações foram salvas."
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
        task_code += 1
        for item in grid:
            sep_new = item["sep_new"]
            if sep_new == str_none:
                none += 1
            elif sep_new != str_remove:  # new sep
                assign.append(item)
            elif item["sep_name"] != str_none:  # ignore remove none
                remove.append(item)

        msg_error = MgmtSepUser.save_grid_view(remove, assign)
    except Exception as e:
        msg_error = str(e)

    return msg_success, msg_error


# eof

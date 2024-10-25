"""
    User Profile's Management and SEP assignment

    Equipe da Canoa -- 2024
    mgd 2024-10-09
"""

# cSpell: ignore mgmt tmpl

import json
from flask import render_template, request

from .models import MgmtUser
from ..helpers.route_helper import get_private_form_data


def do_profile_mgmt() -> str:
    template, is_get, texts = get_private_form_data("profileMgmt")
    grid_value = "7298kjsj0fk9dlsd=)0"
    grid_key = "gridKey"
    grid_data = "gridData"

    if is_get:
        # Até criar ui_texts:
        texts["itemNone"] = "(nenhum)"
        texts["itemRemove"] = "(remover)"
        texts[grid_data] = grid_data
        texts["gridValue"] = grid_value
        texts[grid_key] = grid_key

        users_sep, sep_list, msg_error = MgmtUser.get_grid_view(texts["itemNone"])

        sep_name_list = [sep["name"] for sep in sep_list]
        tmpl = render_template(template, usersSep=users_sep, sepList=sep_name_list, **texts)
    elif request.form.get(grid_key) != grid_value:
        pass
    else:
        gridData = request.form.get(grid_data)
        grid_data = json.loads(gridData)
        print(grid_data)


    return tmpl

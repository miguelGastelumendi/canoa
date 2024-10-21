"""
    User Profile's Management and SEP assignment

    Equipe da Canoa -- 2024
    mgd 2024-10-09
"""

# cSpell: ignore mgmt tmpl

from flask import render_template, request

from .models import MgmtUser
from ..helpers.route_helper import get_private_form_data


def do_profile_mgmt() -> str:
    template, is_get, texts = get_private_form_data("profileMgmt")

    # Até criar ui_texts:
    texts['itemNone'] = "(nenhum)"
    texts['itemRemove'] = "(remover)"

    users_sep, sep_list, msg_error = MgmtUser.get_grid_view(texts['itemNone'])

    sep_name_list = [sep["name"] for sep in sep_list]
    tmpl = render_template(template, usersSep=users_sep, sepList=sep_name_list, **texts)

    return tmpl

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

    none_item = "(nenhum)"
    users_sep, sep_list, msg_error = MgmtUser.get_grid_view(none_item)

    sep_name_list = [sep["name"] for sep in sep_list]
    tmpl = render_template(template, usersSep=users_sep, noneItem=none_item, sepList=sep_name_list, **texts)

    return tmpl

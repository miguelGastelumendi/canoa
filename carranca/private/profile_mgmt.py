"""
    User Profile's Management and SEP assignment

    Equipe da Canoa -- 2024
    mgd 2024-10-09
"""

# cSpell: ignore mgmt tmpl

from flask import render_template, request

from .models import MgmtUser
from ..helpers.route_helper import get_private_form_data, get_input_text


def do_profile_mgmt() -> str:
    template, is_get, texts = get_private_form_data("profileMgmt")

    _users_sep, sep_list, msg_error = MgmtUser.get_grid_view()


    none_str = "(nenhuma)"
    free_sep = [sep["name"] for sep in sep_list]
    free_sep.append(none_str)

    def _free_sep(user):
        sep= user["sep"]
        if sep in free_sep:
            free_sep.remove(sep)
        user["sep"] = none_str if sep is None else sep
        return user

    users_sep = [_free_sep(user) for user in _users_sep]

    # tmpl_form = ReceiveFileForm(request.form)
    tmpl = render_template(template, users_sep=users_sep, sep_list=free_sep, **texts)
    return tmpl

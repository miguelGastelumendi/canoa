"""
    User Profile's Management and SEP assignment

    Equipe da Canoa -- 2024
    mgd 2024-10-09
"""

# cSpell: ignore mgmt tmpl wtforms

import json
from typing import Any, List, Tuple
from flask import render_template, request
from flask_login import current_user

from .models import MgmtSep
from .wtforms import SepEdit
from ..Sidekick import sidekick
from ..helpers.route_helper import get_private_form_data
from ..helpers.ui_texts_helper import add_msg_success, add_msg_error, add_msg_fatal

from ..helpers.route_helper import (
    init_form_vars,
    get_input_text,
)


def do_sep_edit() -> str:
    task_code = 800  # ModuleErrorCode.SEP_EDIT.value
    tmpl_form, template, is_get, uiTexts = init_form_vars()

    task_code += 0
    sep_fullname = "?"
    try:
        task_code += 1  # 1
        user = current_user

        def _get_sep() -> MgmtSep:
            try:
                sep, sep_fullname = (
                    (None, None) if user.mgmt_sep_id is None else MgmtSep.get_sep(user.mgmt_sep_id)
                )
                if sep is None:
                    add_msg_fatal("sepEditNotFound", uiTexts)
            except Exception as e:
                add_msg_fatal("sepEditSelectError", uiTexts)
                sep = None
            return sep, sep_fullname

        task_code += 1  # 2
        template, is_get, uiTexts = get_private_form_data("sepEdit")
        task_code += 1  # 3
        tmpl_form = SepEdit(request.form)
        if is_get:
            task_code = 5
            sep, sep_fullname = _get_sep()
            if sep is not None:
                tmpl_form.name.data = sep_fullname
                tmpl_form.description.data = sep.description
            task_code += 1
        else:
            task_code = 10
            sep, sep_fullname = _get_sep()
            if sep is None:
                add_msg_fatal("sepEditNotFound", uiTexts)
            else:
                task_code += 1
                sep.description = get_input_text("description")
                task_code += 2
                if MgmtSep.set_sep(sep):
                    add_msg_success("sepEditSuccess", uiTexts, sep_fullname)
                else:
                    add_msg_fatal("sepEditFailed", uiTexts, sep_fullname, task_code)

    except Exception as e:
        sidekick.app_log.error(str(e))
        msg = add_msg_fatal("sepEditFailed", uiTexts, sep_fullname, task_code)
        sidekick.Display.error(msg)

    tmpl = render_template(template, form=tmpl_form, **uiTexts)
    return tmpl


# eof

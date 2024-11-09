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

from .models import get_sep
from .wtforms import SepEdit
from ..Sidekick import sidekick
from ..helpers.error_helper import ModuleErrorCode
from ..helpers.py_helper import is_str_none_or_empty
from ..helpers.route_helper import get_private_form_data
from ..helpers.hints_helper import TextsUI
from ..helpers.route_helper import (
    redirect_to,
    login_route,
    init_form_vars,
    get_input_text,
)


def do_sep_edit() -> str:
    task_code = 800  # ModuleErrorCode.SEP_EDIT.value
    tmpl_form, template, is_get, texts = init_form_vars()

    task_code = 0
    try:
        template, is_get, uiTexts = get_private_form_data("sepEdit")
        # Até criar ui_texts:
        uiTexts["formTitle"] = "Edição de SEP"
        uiTexts["pageTitle"] = "Edição de SEP"
        uiTexts["nameLabel"] = "Identificação"
        uiTexts["descriptionLabel"] = "Descrição"
        uiTexts["submitButton"] = "Salvar"
        uiTexts["fileLabel"] = "Imagem [60×60 pixel, formato: png, jpg]"

        tmpl_form = SepEdit(request.form)
        if is_get:
            user = current_user
            sep = None if user.mgmt_sep_id is None else get_sep(user.mgmt_sep_id)
            tmpl_form.name.data = sep.name
            tmpl_form.description.data = sep.description
        else:
            name = "" if is_get else get_input_text("name")
            description = "" if is_get else get_input_text("description")
            # save

        task_code += 1  # 2
        task_code += 1  # 3
        # if is_get:
        #     pass
        # else:

    except Exception as e:
        # msg = add_msg_error("errorPasswordChange", uiTexts, task_code)
        # sidekick.app_log.info(msg)
        sidekick.app_log.error(str(e))
        # TODO: tmpl = render_template(Error)

    tmpl = render_template(template, form=tmpl_form, **uiTexts)

    return tmpl


# eof

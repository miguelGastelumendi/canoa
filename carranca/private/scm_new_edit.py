"""
SEP Edition

Equipe da Canoa -- 2024
mgd 2024-10-09, 11-12
"""

# cSpell: ignore wtforms werkzeug sepsusr usrlist scms nsert

import re
from flask import request
from typing import Optional
from os.path import splitext
from wtforms import StringField
from sqlalchemy import func  # func.now() == server time
from dataclasses import dataclass
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from .wtforms import ScmEdit


from .sep_icon import icon_refresh, ICON_MIN_SIZE
from .SepIconMaker import SepIconMaker
from .sep_constants import SEP_CMD_GRD, SEP_CMD_INS, ACTION_CODE_SEPARATOR
from ..models.private import Sep, Schema, MgmtSepsUser
from ..private.UserSep import UserSep
from ..helpers.py_helper import clean_text, to_int, crc16
from ..public.ups_handler import ups_handler
from ..helpers.user_helper import get_batch_code
from ..helpers.jinja_helper import process_template
from ..helpers.route_helper import (
    get_private_response_data,
    home_route,
    redirect_to,
    init_response_vars,
    get_front_end_str,
)

from ..common.app_context_vars import app_user
from ..common.app_error_assistant import ModuleErrorCode, AppStumbled, JumpOut
from ..helpers.ui_db_texts_helper import (
    UITextsKeys,
    add_msg_success,
    add_msg_error,
    add_msg_final,
)


def do_scm_edit(code: str) -> str:
    """SCM Edit Form"""

    is_insert = code == SEP_CMD_INS

    # edit SEP with ID, is a parameter

    form, tmpl_ffn, is_get, ui_texts = init_response_vars()
    schema_name = "?"
    try:
        task_code = 0
        scm_id = to_int(code, -1)
        tmpl_ffn, is_get, ui_texts = get_private_response_data("scmNewEdit")
        form = ScmEdit(request.form)

        if (scm_row := Schema() if is_insert else Schema.get_row(scm_id)) is None:
            # get the editable row
            # Someone deleted just now?
            raise JumpOut(add_msg_final("scmEditNotFound", ui_texts), task_code + 1)
        schema_name = ui_texts["scmNewTmpName"] if is_insert else scm_row.name

        task_code += 1
        ui_texts["formTitle"] = ui_texts[f"formTitle{'New' if is_insert else 'Edit'}"]
        task_code += 1  # 2

        form.name.render_kw["lang"] = app_user.lang
        form.name.render_kw["pattern"] = "^[a-zA-ZáàãâéêíóôõúüçÁÀÃÂÉÊÍÓÔÕÚÜÇ_]+$"
        form.name.title = "Apenas letras (sem espaço) e underline são permitidos."
        form.title.render_kw["lang"] = app_user.lang
        form.description.render_kw["lang"] = app_user.lang
        form.content.render_kw["lang"] = app_user.lang

        if is_get:
            if is_insert:
                scm_row.id = None
                scm_row.visible = False
                scm_row.color = "#00000"  # RRGGBB
            else:
                for field in form:
                    if hasattr(scm_row, field.name):
                        field.data = getattr(scm_row, field.name)

        else:  # is_post

            def modified(input, field, mod):
                ui_value = (
                    get_front_end_str(input.name, None)
                    if input.type == StringField.__name__
                    else input.data
                )
                _mod = field != ui_value
                if input.data != ui_value:  # TODO, don't change .data
                    input.data = ui_value

                return mod or _mod

            # TODO make a helper
            form_md = is_insert
            for field in form:
                if hasattr(scm_row, field.name):
                    form_md = modified(field, getattr(scm_row, field.name), form_md)

            def _save_and_go():
                form.populate_obj(scm_row)
                #  scm_row.visible = scm_row.visible == "y"  # TODO
                Schema.save(scm_row)
                return redirect_to(home_route())

            schema_name = form.name.data if is_insert else scm_row.name
            if is_insert:
                scm_row.ins_by = app_user.id
                scm_row.ins_at = func.now()
                task_code += 1
                return _save_and_go()
            elif form_md:
                scm_row.edt_by = app_user.id
                scm_row.edt_at = func.now()
                task_code += 2
                return _save_and_go()
            else:
                # TODO Noo modi
                return redirect_to(home_route())

        tmpl = process_template(tmpl_ffn, form=form, **ui_texts)

    except JumpOut:
        tmpl = process_template(tmpl_ffn, **ui_texts)

    except Exception as e:
        item = add_msg_final("scmEditException", ui_texts, schema_name, task_code)
        _, tmpl_ffn, ui_texts = ups_handler(task_code, item, e)
        tmpl = process_template(tmpl_ffn, **ui_texts)

    return tmpl


# eof

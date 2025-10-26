"""
SEP Edition

Equipe da Canoa -- 2024
mgd 2024-10-09, 11-12
"""

# cSpell: ignore wtforms ZáàãâéêíóôõúüçÁÀÃÂÉÊÍÓÔÕÚÜÇ_

from flask import request
from wtforms import StringField
from sqlalchemy import func  # func.now() == db-server time

from .wtforms import ScmEdit
from ..helpers.uiact_helper import UiActResponseProxy

from ..models.private import Schema
from ..public.ups_handler import ups_handler
from ..helpers.jinja_helper import process_template
from ..helpers.route_helper import (
    get_private_response_data,
    init_response_vars,
    get_form_input_value,
    private_route,
    login_route,
    redirect_to,
    home_route,
)

from ..common.app_context_vars import app_user
from ..common.app_error_assistant import ModuleErrorCode, JumpOut
from ..helpers.ui_db_texts_helper import add_msg_final


def do_scm_edit(data: str) -> str:
    """SCM Edit & Insert Form"""

    action, code, row_index = UiActResponseProxy().decode(data)

    if action is not None:  # called from sep_grid
        # TODO use: window.history.back() in JavaScript.
        process_on_end = private_route(
            "scm_grid", code=UiActResponseProxy.show
        )  # TODO selected Row, ix=row_index)
        form_on_close = {"dlg_close_action_url": process_on_end}

    else:  # standard routine
        code = data
        action = None
        process_on_end = login_route()  # default
        form_on_close = {}  # default = login

    is_insert = code == UiActResponseProxy.add
    is_edit = not is_insert

    # edit SEP with ID, is a parameter
    new_scm_id = 0
    scm_id = new_scm_id if is_insert else Schema.to_id(code)

    task_code = ModuleErrorCode.SCM_EDIT.value
    form, tmpl_rfn, is_get, ui_texts = init_response_vars()
    schema_name = "?"
    tmpl = ""
    try:
        task_code += 1
        tmpl_rfn, is_get, ui_texts = get_private_response_data("scmNewEdit")
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
        form.name.render_kw["pattern"] = ui_texts["nameInputPattern"]
        form.name.render_kw["title"] = ui_texts["nameErrorHint"]

        form.description.render_kw["lang"] = app_user.lang
        form.content.render_kw["lang"] = app_user.lang
        form.title.render_kw["lang"] = app_user.lang

        if is_get and is_insert:
            scm_row.id = None
            scm_row.visible = False
            scm_row.color = ui_texts["colorDefaultValue"]  # "#00000"  # RR GG BB
        elif is_get and is_edit:
            for field in form:
                if hasattr(scm_row, field.name):
                    field.data = getattr(scm_row, field.name)
        else:  # is_post
            def _modified(input, field, is_mod):
                ui_value = (
                    get_form_input_value(input.name, None)
                    if input.type == StringField.__name__
                    else input.data
                )
                _mod = field != ui_value
                if input.data != ui_value:  # TODO, don't change .data
                    input.data = ui_value

                return is_mod or _mod

            # TODO make a helper
            form_md = is_insert
            for field in form:
                if hasattr(scm_row, field.name):
                    form_md = _modified(field, getattr(scm_row, field.name), form_md)

            def _save_and_go():
                form.populate_obj(scm_row)
                #  scm_row.visible = scm_row.visible == "y"  # TODO
                scm_row.color = scm_row.color.upper()
                Schema.save(scm_row)
                return redirect_to(process_on_end)
                # return redirect_to(home_route())

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
                # TODO Not modi
                return redirect_to(home_route())

        tmpl = process_template(tmpl_rfn, form=form, **ui_texts, **form_on_close)

    except JumpOut:
        tmpl = process_template(tmpl_rfn, **ui_texts)

    except Exception as e:
        item = add_msg_final("scmEditException", ui_texts, schema_name, task_code)
        _, tmpl_rfn, ui_texts = ups_handler(task_code, item, e)
        tmpl = process_template(tmpl_rfn, **ui_texts)

    return tmpl


# eof

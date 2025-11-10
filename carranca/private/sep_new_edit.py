"""
SEP Edition

Equipe da Canoa -- 2024
mgd 2024-10-09, 11-12
mgd 2025-08-19--22  allow edit manager
"""

# cSpell: ignore wtforms werkzeug sepsusr usrlist scms nsert

import re
from flask import request
from typing import Tuple, cast
from os.path import splitext
from sqlalchemy import func  # func.now() == server time
from dataclasses import dataclass
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from .wtforms import SepEdit, SepNew
from .sep_icon import icon_refresh, ICON_MIN_SIZE
from .SepIconMaker import SepIconMaker
from .sep_form_data import get_sep_data, SepEditMode, NoManager
from ..models.private import Sep
from ..private.UserSep import UserSep
from ..helpers.py_helper import is_str_none_or_empty, to_int, crc16
from ..public.ups_handler import ups_handler
from ..helpers.user_helper import get_batch_code
from ..helpers.types_helper import UsualDict
from ..helpers.uiact_helper import UiActResponseProxy
from ..helpers.jinja_helper import process_template
from ..common.app_context_vars import app_user
from ..helpers.js_consts_helper import js_form_sec_check, js_ui_dictionary
from ..common.app_error_assistant import ModuleErrorCode, AppStumbled, JumpOut
from ..helpers.route_helper import (
    get_private_response_data,
    init_response_vars,
    get_form_input_value,
    private_route,
    login_route,
    redirect_to,
)
from ..helpers.ui_db_texts_helper import (
    UITextsKeys,
    add_msg_success,
    add_msg_error,
    add_msg_final,
)


def do_sep_edit(data: str) -> str:
    """SEP Edit & Insert Form"""

    SVG_MIME = "image/svg+xml"
    @dataclass
    class IconData:
        content: str = ""
        file_name: str = ""
        ready: bool = False
        crc: int = 0
        error_hint: str = ""
        error_code: int = 0

    action, code, row_index = UiActResponseProxy().decode(data)

    if action is not None:  # called from sep_grid
        # TODO use: window.history.back() in JavaScript.
        process_on_end = private_route(
            "sep_grid", code=UiActResponseProxy.show
        )  # TODO selected Row, ix=row_index)
        form_on_close = {"dlg_close_action_url": process_on_end}

    else:  # standard routine
        code = data
        action = None
        process_on_end = login_route()  # default
        form_on_close = {}  # default = login

    editMode = SepEditMode.NONE
    edit_full_or_ins = True
    if (code == UiActResponseProxy.add):
        editMode = SepEditMode.INSERT
    elif app_user.is_power:  #  and is_edit
        editMode = SepEditMode.FULL_EDIT
    else:
        # `normal user` can only edit description & icon
        editMode = SepEditMode.SIMPLE_EDIT
        edit_full_or_ins = False



    # edit SEP with ID, is a parameter
    new_sep_id = 0
    sep_id = new_sep_id if (editMode == SepEditMode.INSERT) else UserSep.to_id(code)
    if sep_id is None or sep_id < 0:
        return redirect_to(process_on_end)

    task_code = ModuleErrorCode.SEP_EDIT.value
    tmpl, is_get, ui_db_texts = init_response_vars()
    # &#8209 is a `nobreak-hyphen`, &hyphen does not work.
    sep_fullname = f"SPC&#8209;{code}"
    form: UsualDict = {}
    try:
        no_manager = NoManager()
        js_ui_dict = js_ui_dictionary()

        def was_icon_file_sent() -> Tuple[bool, FileStorage | None]:
            form_file_name = form.icon_filename.name
            file_storage: FileStorage = (
                request.files[form_file_name]
                if form_file_name in request.files
                else None
            )
            icon_file_sent = (
                file_storage is not None
                and file_storage.content_type.startswith(SVG_MIME)
            )
            return icon_file_sent, file_storage

        def _was_form_sep_modified(sep_row: Sep) -> Tuple[bool, bool, int, int]:
            # remove schema/sep separator sep+sep
            ui_sep_name = get_form_input_value(form.sep_name.name, [Sep.scm_sep])
            ui_description = get_form_input_value(form.description.name)
            frm_id_manager = cast(int, form.manager_list.data)
            id_manager = frm_id_manager if edit_full_or_ins and not (frm_id_manager == no_manager.id) else -1

            if (editMode == SepEditMode.INSERT):
                id_schema = cast(int, form.schema_list.data)
                sep_modified = True
                form_modified = cast(bool, id_manager or id_schema or ui_description or ui_sep_name)
            else:
                # SepEditMode.FULL_EDIT or SepEditMode.SIMPLE_EDIT
                # TODO check Schema
                sep_name = sep_row.name if ui_sep_name is None else ui_sep_name
                form.sep_name.data = sep_name
                id_schema = cast(int, form.schema_list.data if editMode == SepEditMode.FULL_EDIT else sep_row.id_schema)
                sep_modified = not (sep_name == sep_row.name)
                form_modified = cast(bool,
                    sep_modified
                    or (id_manager != sep_row.users_id)
                    or (ui_description != sep_row.description)
                    or (id_schema != sep_row.id_schema)
                    or (form.visible.data != sep_row.visible)
                    or was_icon_file_sent()[0]  # keep it as the last test (resource)
                )

            # remove spaces & '/' (scm_sep) so the user see its modified values (see get_input_text)
            form.description.data = ui_description
            form.sep_name.data = ui_sep_name
            return form_modified, sep_modified, id_schema, id_manager

        def _get_icon_data(sep_row: Sep) -> IconData:
            def __find(pattern: str, data: str) -> int:
                match = re.search(pattern, data, re.IGNORECASE | re.DOTALL)
                return match.start() if match else -1

            icon_file_sent, file_storage = was_icon_file_sent()
            icon_data = IconData(file_name=file_storage.filename)
            expected_ext = f".{SepIconMaker.ext}".lower()

            if not icon_file_sent:
                pass
            elif not splitext(icon_data.file_name)[1].lower().endswith(expected_ext):
                icon_data.error_hint = expected_ext
                icon_data.error_code = 1
            elif not (file_obj := request.files.get(form.icon_filename.name)):
                icon_data.error_hint = "↑×"
                icon_data.error_code = 2
            elif len(data := file_obj.read().decode("utf-8").strip()) < ICON_MIN_SIZE:
                icon_data.error_hint = f"≤ {ICON_MIN_SIZE}"
                icon_data.error_code = 3
            elif (start := __find(r"<svg.*?>", data)) < 0:
                icon_data.error_hint = "¿<svg>"
                icon_data.error_code = 4
            elif (end := __find(r"</svg\s*>", data)) < 0:
                icon_data.error_hint = "</svg>?"
                icon_data.error_code = 5
            elif (end - start) < ICON_MIN_SIZE:
                icon_data.error_hint = f"< {ICON_MIN_SIZE}"
                icon_data.error_code = 6
            elif not (sep_row.icon_svg or "") == (data or ""):
                icon_data.content = data
                icon_data.crc = crc16(data)
                icon_data.ready = True

            return icon_data

        task_code += 1  # 1
        tmpl_rfn, is_get, ui_db_texts = get_private_response_data("sepNewEdit")
        no_manager = NoManager(name= ui_db_texts["mng_placeholderOption"])

        ui_db_texts["formForNew"] = edit_full_or_ins
        ui_db_texts["formTitle"] = ui_db_texts[f"formTitle{('New' if editMode == SepEditMode.INSERT else 'Edit')}"]
        task_code += 1  # 2
        form = SepNew(request.form) if edit_full_or_ins else SepEdit(request.form)
        # Personalized template for this user (see tmpl_form.sep_name for more info):
        input_disabled = not app_user.is_power
        form.sep_name.render_kw["disabled"] = input_disabled
        form.sep_name.render_kw["required"] = not input_disabled
        form.sep_name.render_kw["lang"] = app_user.lang
        form.description.render_kw["lang"] = app_user.lang

        task_code += 1  # 3
        task_code, usr_sep, sep_row, select_lists, sep_fullname = get_sep_data(task_code, editMode, no_manager, ui_db_texts, sep_id, form, sep_fullname)

        task_code = ModuleErrorCode.SEP_EDIT.value + 10  # 510
        form_mod, sep_mod, id_schema, id_manager = (
            (False, False, -1, -1) if is_get else _was_form_sep_modified(sep_row)
        )

        sep_name = usr_sep.name if input_disabled else form.sep_name.data

        if is_get:
            task_code += 1
        elif not form_mod:
            # TODO: nothing modified, add_msg_warn("nothingChanged", ui_texts)
            return redirect_to(process_on_end)
        elif not is_str_none_or_empty(msg_error:= js_form_sec_check()):
            task_code += 2
            msg_error = add_msg_error(msg_error, ui_db_texts)
            raise AppStumbled(msg_error, task_code, True, True)
        elif (scm_name:= next((scm["name"] for scm in select_lists.schemaList if scm["id"] == id_schema), "?")) is None:
            # should never happen
            pass
        elif ((editMode == SepEditMode.INSERT) or sep_mod) and Sep.full_name_exists(id_schema, sep_name):
            add_msg_error("sepNameRepeated", ui_db_texts, scm_name, sep_name)
        elif (icon_data := _get_icon_data(sep_row)).error_code > 0:
            # msg {ext} [{hint}-{code}]
            add_msg_error(
                "sepEditInvalidFormat",
                ui_db_texts,
                SepIconMaker.ext,
                icon_data.error_hint,
                icon_data.error_code,
            )
        # TODO: Check if icon used (CRC) in other SEP, index is ready
        else:
            task_code += 1  # 511
            sep_row.name = sep_name
            sep_row.visible = bool(form.visible.data)
            sep_row.description = get_form_input_value(form.description.name)
            batch_code = get_batch_code()

            if (editMode == SepEditMode.INSERT):
                icon_old_file_name = None
                sep_row.id = None
                sep_row.visible = True
                sep_row.id_schema = id_schema
                sep_row.ins_by = app_user.id
                sep_row.ins_at = func.now()
            else:
                icon_old_file_name = sep_row.icon_file_name
                sep_row.edt_by = app_user.id
                sep_row.edt_at = func.now()

            if edit_full_or_ins:
                task_code += 1  # 512
                # we need `sep_fullname`` in case of error (see except)
                sep_fullname = Sep.get_fullname(scm_name, sep_row.name)
                sep_row.users_id = id_manager

            if schema_changed := ((editMode == SepEditMode.FULL_EDIT) and (id_schema != sep_row.id_schema)):
                sep_row.id_schema = id_schema

            icon_new_file_name = None
            if fresh_icon := icon_data.ready:
                task_code += 4  # 516
                sep_row.icon_svg = icon_data.content
                sep_row.icon_crc = icon_data.crc
                sep_row.icon_file_name = (
                    f"{batch_code}-{icon_data.crc:04x}_sep.{SepIconMaker.ext}"
                )
                sep_row.icon_uploaded_at = func.now()
                sep_row.icon_original_name = secure_filename(icon_data.file_name)
                sep_row.ico_by = app_user.id
                sep_row.ico_at = func.now()
                sep_row.icon_version = to_int(sep_row.icon_version, 0) + 1
                ui_db_texts[UITextsKeys.Form.icon_url] = SepIconMaker.get_url(
                    sep_row.icon_file_name
                )
                icon_new_file_name = sep_row.icon_file_name

            if (sep_id := Sep.save(sep_row, schema_changed, batch_code)) >= 0:  # :——)
                task_code += 5  # 21
                add_msg_success(
                    "sepSuccessNew" if editMode == SepEditMode.INSERT else "sepSuccessEdit",
                    ui_db_texts,
                    sep_fullname,
                )
                if fresh_icon:  # after post
                    icon_refresh(icon_old_file_name, icon_new_file_name, sep_id)
                if action:
                    return redirect_to(process_on_end)
            else:  # :——(
                task_code += 6  # 19
                item = f"sepFailed{'Edit' if editMode == SepEditMode.SIMPLE_EDIT else 'New'}"
                add_msg_final(item, ui_db_texts, sep_fullname, task_code)

        tmpl = process_template(tmpl_rfn, form=form, **ui_db_texts.dict(), **select_lists,  **js_ui_dict, **form_on_close, )

    except JumpOut:
        tmpl = process_template(tmpl_rfn, **ui_db_texts)

    except AppStumbled as e:
        _, tmpl_rfn, ui_db_texts = ups_handler(task_code, '',  e)
        tmpl = process_template(tmpl_rfn, **ui_db_texts)

    except Exception as e:
        item = add_msg_final("sepEditException", ui_db_texts, sep_fullname, task_code)
        _, tmpl_rfn, ui_db_texts = ups_handler(task_code, item, e)
        tmpl = process_template(tmpl_rfn, **ui_db_texts)

    return tmpl


# eof

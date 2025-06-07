"""
SEP Edition

Equipe da Canoa -- 2024
mgd 2024-10-09, 11-12
"""

# cSpell: ignore tmpl wtforms werkzeug sepsusr usrlist scms nsert

from flask import render_template, request
from typing import Tuple
from os.path import splitext
from dataclasses import dataclass
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from ..models.private import Sep, Schema, MgmtSepsUser
from .wtforms import SepEdit, SepNew

from .UserSep import UserSep
from .sep_icon import icon_refresh, ICON_MIN_SIZE
from .sep_constants import SEP_CMD_GRD, SEP_CMD_INS, ACTION_CODE_SEPARATOR
from .SepIconConfig import SepIconConfig
from ..public.ups_handler import ups_handler
from ..helpers.py_helper import now, to_int, crc16
from ..helpers.route_helper import (
    get_private_response_data,
    init_response_vars,
    get_input_text,
    login_route,
    private_route,
    redirect_to,
)

from ..common.app_context_vars import app_user
from ..common.app_error_assistant import ModuleErrorCode, AppStumbled, JumpOut
from ..helpers.ui_db_texts_helper import (
    UITextsKeys,
    add_msg_success,
    add_msg_error,
    add_msg_final,
)


SVG_MIME = "image/svg+xml"


def do_sep_edit(data: str) -> str:
    """SEP Edit Form"""

    @dataclass
    class IconData:
        content: str = ""
        file_name: str = ""
        ready: bool = False
        crc: int = 0
        error_code: int = 0

    new_sep_id = 0

    if ACTION_CODE_SEPARATOR in data:  # called from sep_grid
        """
        action:code
        -----------
        `action` can be:
            » None: is a call from the menu, no action.
              After edit or insert, return to standard login()
                or
            » [C]reate, [I]nsert, [E]dit
            It is the first char of the button that trigger the action in
                `private\sep_grid.html.j2`
            and routed here via
                `private/rout("/sep_grid/<code>")`
            See sep_grid.html.j2  { -- Action Triggers -- }
            After edit or insert, return to the calling grid & select this row
        """
        action = data.split(ACTION_CODE_SEPARATOR)[0]

        """
        `code` can be:
            » SEP_CMD_INS : insert a new SEP
              or
            » The obfuscate ID of the SEP to edit
        """
        code = data.split(ACTION_CODE_SEPARATOR)[1]
        """
            Where to go after
            save: goto
            close: on_close
        """
        process_on_end = private_route("sep_grid", code=SEP_CMD_GRD)
        from_on_close = {"action_form__form_on_close": process_on_end}

    else:  # standard routine
        code = data
        action = None
        process_on_end = login_route()  # default
        from_on_close = {}  # default = login

    is_new_form = code == SEP_CMD_INS
    is_edit_form = not is_new_form
    sep_id = new_sep_id if is_new_form else UserSep.to_id(code)
    if sep_id is None or sep_id < 0:
        return redirect_to(process_on_end)

    task_code = ModuleErrorCode.SEP_EDIT.value
    flask_form, tmpl_ffn, is_get, ui_texts = init_response_vars()
    sep_fullname = f"SPC&#8209;{code}"  # &#8209 is a `nobreak-hyphen`, &hyphen does not work.

    try:

        def _icon_file_sent() -> Tuple[bool, FileStorage | None]:
            form_file_name = flask_form.icon_filename.name
            file_storage: FileStorage = (
                request.files[form_file_name] if form_file_name in request.files else None
            )
            icon_file_sent = file_storage is not None and file_storage.content_type.startswith(SVG_MIME)
            return icon_file_sent, file_storage

        def _get_sep_data(load_sep_icon_content: bool, task_code: int) -> Tuple[UserSep, Sep, int, str]:
            if is_edit_form:
                task_code += 1  # 1
            elif not app_user.is_power:  # and is_new_form
                raise AppStumbled(add_msg_final("sepNewNotAllow", ui_texts), task_code, True)
            else:  # is_new_form
                # prepare the Select Schema (available for power in insertion)
                task_code += 1  # 1
                select_one = ui_texts["placeholderOption"]
                ui_texts["schemaList"] = [{"id": "", "name": select_one}] + Schema.get_schemas().to_list()
                ui_texts["schemaListValue"] = "" if is_get else flask_form.schema_list.data
                ui_texts[UITextsKeys.Form.icon_url] = SepIconConfig.get_icon_url(SepIconConfig.empty_file)
                sep_row = Sep()
                return None, sep_row, task_code, ui_texts["sepNewTmpName"]  # 4

            # --- is_edit_form ---
            # --------------------
            task_code += 1  # 2
            usr_sep = next((sep for sep in app_user.seps if sep.id == sep_id), None)
            if usr_sep is not None:
                sep_usr_rows = MgmtSepsUser.get_user_sep_list(app_user.id)
            elif not app_user.is_power:
                raise JumpOut(add_msg_final("sepEditNotAllow", ui_texts, sep_fullname), task_code)
            elif (sep_usr_rows := MgmtSepsUser.get_sep(sep_id)) is None or (sep_usr_rows.count == 0):
                raise JumpOut(add_msg_final("sepEditNotFound", ui_texts), task_code + 2)  # 7
            else:
                edit_dict = dict(sep_usr_rows[0])
                # Remove 'user_curr' from edit_dict, because is not needed in UserSep(..)
                sep_manager = edit_dict.pop("user_curr", None)
                usr_sep = UserSep(**edit_dict)

            # check permissions
            if sep_usr_rows is None:
                """
                This condition seems unlikely to be met if get_user_sep_list returns
                a list or None as per its likely contract.
                Consider if this check is necessary or if the next one covers it.
                """
                raise JumpOut(add_msg_final("sepEditNotAllow", ui_texts), task_code + 1)  # 5
            elif None == (sep_user_row := next((mus for mus in sep_usr_rows if mus.id == sep_id), None)):
                raise JumpOut(add_msg_final("sepEditNotAllow", ui_texts), task_code + 2)  # 6
            elif (sep_row := Sep.get_sep(sep_id, load_sep_icon_content)) is None:
                raise JumpOut(add_msg_final("sepEditNotFound", ui_texts), task_code + 3)  # 7
            elif is_get:
                # set the form's data row for edition
                flask_form.schema_name.data = usr_sep.scm_name  # readonly
                flask_form.sep_name.data = sep_row.name
                flask_form.description.data = sep_row.description
                flask_form.icon_filename.data = None
                task_code += 8  # 513

            # set the icon
            # task_code += 1  # 3
            # ui_texts[UITextsKeys.Form.icon_url] = usr_sep.icon_url

            return usr_sep, sep_row, task_code, sep_user_row.fullname

        def _get_id_schema() -> int:
            lst_name = flask_form.schema_list.name
            id_schema = int(request.form.get(lst_name, -1)) if is_new_form else None
            return id_schema

        def _form_modified(sep_row: Sep) -> bool:
            # remove schema/sep separator sep+sep
            ui_description = get_input_text(flask_form.description.name)
            ui_sep_name = get_input_text(flask_form.sep_name.name, [Sep.scm_sep])

            if is_new_form:
                id = flask_form.schema_list.data
                form_modified = id or ui_description or ui_sep_name or _icon_file_sent()[0]
            else:  # is_edit and maybe user cannot modified sep_name
                # TODO check Schema
                sep_name = sep_row.name if ui_sep_name is None else ui_sep_name
                flask_form.sep_name.data = sep_name
                form_modified = (
                    (sep_name != sep_row.name)
                    or (ui_description != sep_row.description)
                    or _icon_file_sent()[0]  # keep it as the last test
                )

            # remove spaces & '/' (scm_sep) so the user see its modified values (see get_input_text)
            flask_form.description.data = ui_description
            flask_form.sep_name.data = ui_sep_name
            return form_modified

        def _get_icon_data(sep_row: Sep) -> IconData:
            icon_file_sent, file_storage = _icon_file_sent()
            icon_data = IconData(file_name=file_storage.filename)
            expected_ext = f".{SepIconConfig.ext}".lower()

            if not icon_file_sent:
                pass
            elif not splitext(icon_data.file_name)[1].lower().endswith(expected_ext):
                icon_data.error_code = 1
            elif not (file_obj := request.files.get(flask_form.icon_filename.name)):
                icon_data.error_code = 2
            elif len(data := file_obj.read().decode("utf-8").strip()) < ICON_MIN_SIZE:
                icon_data.error_code = 3
            elif (start := (idx if (idx := data.find("<svg>")) != -1 else data.find("<svg "))) < 0:
                icon_data.error_code = 4
            elif (end := data.find("</svg>")) < 0:
                icon_data.error_code = 5
            elif (end - start) < ICON_MIN_SIZE:
                icon_data.error_code = 6
            elif not (sep_row.icon_svg or "") == (data or ""):
                icon_data.content = data
                icon_data.crc = crc16(data)
                icon_data.ready = True

            return icon_data

        task_code += 1  # 2
        tmpl_ffn, is_get, ui_texts = get_private_response_data("sepNewEdit")
        ui_texts["formForNew"] = is_new_form
        ui_texts["formTitle"] = ui_texts[f"formTitle{('Edit' if is_edit_form else 'New')}"]
        task_code += 1  # 2
        flask_form = SepNew(request.form) if is_new_form else SepEdit(request.form)
        # Personalized template for this user (see tmpl_form.sep_name for more info):
        input_disabled = not app_user.is_power
        flask_form.sep_name.render_kw["required"] = not input_disabled
        flask_form.sep_name.render_kw["disabled"] = input_disabled
        flask_form.sep_name.render_kw["lang"] = app_user.lang
        flask_form.description.render_kw["lang"] = app_user.lang

        task_code += 1  # 3
        usr_sep, sep_row, task_code, sep_fullname = _get_sep_data(not is_get, task_code)

        task_code = ModuleErrorCode.SEP_EDIT.value + 10
        sep_name = flask_form.sep_name.data
        if is_get:
            task_code += 1
        elif not _form_modified(sep_row):
            # TODO: nothing modified, add_msg_warn("nothingChanged", ui_texts)
            return redirect_to(process_on_end)
        elif is_new_form and Sep.this_name_exists(sep_name):
            add_msg_error("sepNameRepeated", ui_texts, sep_name)
        elif (icon_data := _get_icon_data(sep_row)).error_code > 0:
            add_msg_error("sepEditInvalidFormat", ui_texts, SepIconConfig.ext, icon_data.error_code)
        else:
            task_code += 1
            sep_row.name = sep_name
            sep_row.description = get_input_text(flask_form.description.name)
            if is_new_form:
                task_code += 1  #
                sep_row.visible = True
                sep_row.ins_by = app_user.id
                lst_name = flask_form.schema_list.name
                sep_row.id_schema = int(request.form.get(lst_name, -1)) if is_new_form else None
                sep_row.id = None
                scm_list = ui_texts["schemaList"]
                scm_name = next((scms["name"] for scms in scm_list if scms["id"] == sep_row.id_schema), "?")
                # get sep_fullname in case of error
                sep_fullname = Sep.get_fullname(scm_name, sep_row.name)

            if new_icon := icon_data.ready:
                task_code += 2
                sep_row.icon_original_name = secure_filename(icon_data.file_name)
                sep_row.icon_file_name = f"{app_user.code}u-{icon_data.crc:04x}_sep.{SepIconConfig.ext}"
                sep_row.icon_uploaded_at = now()
                sep_row.icon_svg = icon_data.content
                iv = sep_row.icon_version
                sep_row.icon_version = iv + 1 if to_int(iv, 0) > 0 else 1
                ui_texts[UITextsKeys.Form.icon_url] = SepIconConfig.get_icon_url(sep_row.icon_file_name)

            if Sep.save(sep_row):  # Success  :—)
                task_code += 3  # 18
                add_msg_success("sepEditSuccess", ui_texts, sep_fullname)
                if new_icon and usr_sep:  # after post
                    icon_refresh(usr_sep)  # refresh this form icon

                if action:
                    return redirect_to(process_on_end)

            else:  # :—(
                task_code += 4  # 19
                item = f"sepFailed{'Edit' if is_edit_form else 'New'}"
                add_msg_final(item, ui_texts, sep_fullname, task_code)

    except JumpOut:
        pass
    except Exception as e:
        item = add_msg_final("sepEditException", ui_texts, sep_fullname, task_code)
        _, tmpl_ffn, ui_texts = ups_handler(task_code, item, e)
        tmpl = render_template(tmpl_ffn, **ui_texts)

    # ??  import pdb; pdb.set_trace()  # Pause here to inspect `context`
    tmpl = render_template(tmpl_ffn, form=flask_form, **ui_texts, **from_on_close)
    return tmpl


# eof

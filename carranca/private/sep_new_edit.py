"""
SEP Edition

Equipe da Canoa -- 2024
mgd 2024-10-09, 11-12
"""

# cSpell: ignore tmpl wtforms werkzeug sepsusr usrlist scms

from flask import render_template, request
from typing import Tuple
from os.path import splitext
from collections import namedtuple
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from ..models.private import Sep, Schema, MgmtSepsUser
from .wtforms import SepEdit, SepNew

from .UserSep import UserSep
from .SepIconConfig import SepIconConfig
from ..public.ups_handler import ups_handler
from ..helpers.py_helper import now, to_int, crc16
from ..helpers.route_helper import (
    get_private_form_data,
    init_form_vars,
    get_input_text,
    login_route,
    redirect_to,
)

from ..common.app_context_vars import app_user, sidekick
from ..common.app_error_assistant import ModuleErrorCode, AppStumbled
from ..helpers.ui_db_texts_helper import (
    UITextsKeys,
    add_msg_success,
    add_msg_error,
    add_msg_fatal,
)


def do_sep_edit(code: str) -> str:
    """SEP Edit Form"""
    IconData = namedtuple("IconData", ["content", "file_name", "ready", "crc", "error_code"])

    ICON_MIN_SIZE = 267
    sep_sep = sidekick.config.SCM_SEP_SEPARATOR
    new_sep_code = "add"
    new_sep_id = 0
    is_new = code == new_sep_code
    is_edit = not is_new
    sep_id = new_sep_id if is_new else UserSep.to_id(code)
    if sep_id is None or sep_id < 0:
        return redirect_to(login_route())

    task_code = ModuleErrorCode.SEP_EDIT.value
    tmpl_form, template, is_get, ui_texts = init_form_vars()
    sep_fullname = f"SPC&#8209;{code}"  # &#8209 is a `nobreak-hyphen`, &hyphen does not work.
    try:

        def _file_sent() -> Tuple[bool, str]:
            file_input_name = tmpl_form.icon_filename.name
            file_storage: FileStorage = (
                request.files[file_input_name] if file_input_name in request.files else None
            )
            file_sent = file_storage is not None and file_storage.content_length > ICON_MIN_SIZE
            return file_sent, file_storage

        def _get_sep_data(load_sep_content: bool, task_code: int) -> Tuple[UserSep, Sep, int, str]:
            if is_edit:
                task_code += 1  # 1
            elif not app_user.is_power:  # and is new sep
                raise AppStumbled(add_msg_fatal("sepNewNotAllow", ui_texts), task_code)
            else:
                # prepare the Select Schema (available for power)
                task_code += 1  # 1
                select_one = ui_texts["placeholderOption"]
                ui_texts["schemaList"] = [{"id": "", "name": select_one}] + Schema.get_schemas().to_list()
                ui_texts["schemaListValue"] = "" if is_get else tmpl_form.schema_list.data
                ui_texts[UITextsKeys.Form.icon_url] = SepIconConfig.get_icon_url(SepIconConfig.empty_file)
                sep_row = Sep()
                return None, sep_row, task_code, ui_texts["sepNewTmpName"]  # 4

            # --- is edit ---
            # ---------------
            task_code += 1  # 2
            usr_sep = next((sep for sep in app_user.seps if sep.id == sep_id), None)
            if usr_sep is None:
                raise AppStumbled(add_msg_fatal("sepEditNotAllow", ui_texts), task_code)

            # set the icon
            task_code += 1  # 3
            ui_texts[UITextsKeys.Form.icon_url] = usr_sep.icon_url

            # is user in the db 'permission table'?
            task_code += 1  # 4
            sep_usr_rows, _ = MgmtSepsUser.get_sepsusr_and_usrlist(app_user.id)

            # check permissions
            if sep_usr_rows is None:
                raise AppStumbled(add_msg_fatal("sepEditNotAllow", ui_texts), task_code + 1)  # 5
            elif None == (sep_user_row := next((mus for mus in sep_usr_rows if mus.id == sep_id), None)):
                raise AppStumbled(add_msg_fatal("sepEditNotAllow", ui_texts), task_code + 2)  # 6
            elif (sep_row := Sep.get_sep(sep_id, load_sep_content)) is None:
                raise AppStumbled(add_msg_fatal("sepEditNotFound", ui_texts), task_code + 3)  # 7
            elif is_get:
                # get the Sep table data row to edit
                tmpl_form.schema_list.data = None  # used when id NewForm
                tmpl_form.schema_name.data = None if is_new else usr_sep.scm_name
                tmpl_form.sep_name.data = sep_row.name
                tmpl_form.description.data = sep_row.description
                tmpl_form.icon_filename.data = None
                task_code += 8  # 506

            return usr_sep, sep_row, task_code, sep_user_row.fullname

        def _form_modified(is_new: bool, sep_row: Sep) -> bool:
            sep_name = get_input_text(tmpl_form.sep_name.name, [sep_sep])
            description = get_input_text(tmpl_form.description.name)

            if is_new:
                same_form = False
            else:
                file_sent, _ = _file_sent()
                same_form = (
                    (sep_name == sep_row.name) and (description == sep_row.description) and not file_sent
                )

            # remove spaces & '/' (sep_sep)  so the user see its modified values
            tmpl_form.sep_name.data = sep_name
            tmpl_form.description.data = description
            return not same_form

        def _get_icon_data(is_edit: bool, sep_row: Sep) -> IconData:
            file_sent, file_storage = _file_sent()
            icon_data = IconData(content="", file_name="", crc=0, ready=False, error_code=0)

            if not file_sent:
                pass
            elif not (splitext(file_storage.filename)[1].lower() == SepIconConfig.ext.lower()):
                icon_data.error_code = 1
            elif not (file_obj := request.files.get(file_storage.filename)):
                icon_data.error_code = 2
            elif file_storage.content_type.find("svg") < 0:
                icon_data.error_code = 3
            # fmt: off
            elif not ((data:= file_obj.read().decode("utf-8")) and len(data:= data.strip()) > ICON_MIN_SIZE):
                icon_data.error_code = 4
            elif (start := data.find("<svg>")) < 0 or (end := data.find("</svg>")) < 0 or (end - start) < ICON_MIN_SIZE:
                # fmt: on
                icon_data.error_code = 5
            else:
                same_content = (sep_row.icon_svg or "") == (data or "")
                icon_data.file_name = file_storage.filename
                icon_data.content = "" if same_content else data
                icon_data.crc = 0 if same_content else crc16(data)
                icon_data.ready = not same_content

            return icon_data

        task_code += 1  # 2
        template, is_get, ui_texts = get_private_form_data("sepNewEdit")
        ui_texts["formForNew"] = is_new
        ui_texts["formTitle"] = ui_texts[f"formTitle{('Edit' if is_edit else 'New')}"]
        ui_texts["schemaLabel"] = ui_texts[("schemaLabel" if is_edit else "schemasLabel")]
        task_code += 1  # 2
        tmpl_form = SepEdit(request.form) if is_edit else SepNew(request.form)

        task_code += 1  # 3
        usr_sep, sep_row, task_code, sep_fullname = _get_sep_data(not is_get, task_code)

        task_code = ModuleErrorCode.SEP_EDIT.value + 10
        if is_get:
            task_code += 1
        elif not _form_modified(is_new, sep_row):
            # TODO: nothing modified, add_msg_warn("nothing", ui_texts)
            return redirect_to(login_route())
        elif is_new and Sep.this_name_exists(sep_name := tmpl_form.sep_name.data):
            add_msg_error("sepNameRepeated", ui_texts, sep_name)
        elif (icon_data := _get_icon_data(is_edit, sep_row)).error_code > 0:
            add_msg_error("sepEditInvalidFormat", ui_texts, SepIconConfig.ext, icon_data.error_code)
        else:
            task_code += 1
            sep_row.description = get_input_text(tmpl_form.description.name)
            if is_new:
                task_code += 1  #
                sep_row.visible = True
                sep_row.ins_by = app_user.id
                sep_row.id_schema = (
                    int(request.form.get(tmpl_form.schema_list.name, -1)) if is_new else None
                )
                sep_row.name = sep_name
                sep_row.id = None
                # get sep_fullname in case of error
                scm_list = ui_texts["schemaList"]
                scm_name = next((scms["name"] for scms in scm_list if scms["id"] == sep_row.id_schema), "?")
                sep_fullname = f"{scm_name}{sep_sep}{sep_row.name}"

            if new_icon := icon_data.ready:
                task_code += 2
                sep_row.icon_original_name = secure_filename(icon_data.file_name)
                sep_row.icon_file_name = f"{app_user.code}u-{icon_data.crc:x04}sep.{SepIconConfig.ext}"
                sep_row.icon_uploaded_at = now()
                sep_row.icon_svg = icon_data.content
                iv = sep_row.icon_version
                sep_row.icon_version = iv + 1 if to_int(iv, 0) > 0 else 1
                ui_texts[UITextsKeys.Form.icon_url] = SepIconConfig.get_icon_url(sep_row.icon_file_name)

            if not Sep.set_sep(sep_row):
                task_code += 3  # 18
                item = f"sepFailed{'Edit' if is_edit else 'New'}"
                add_msg_fatal(item, ui_texts, sep_fullname, task_code)
            else:
                task_code += 4  # 19
                add_msg_success("sepEditSuccess", ui_texts, sep_fullname)
                if new_icon and usr_sep:  # after post
                    from .sep_icon import icon_refresh

                    icon_refresh(usr_sep)  # refresh this form icon

    except Exception as e:
        # task_code +=
        item = add_msg_fatal("sepEditException", ui_texts, sep_fullname, task_code)
        _, template, ui_texts = ups_handler(task_code, item, e)
        tmpl = render_template(template, **ui_texts)

    # ??  import pdb; pdb.set_trace()  # Pause here to inspect `context`
    tmpl = render_template(template, form=tmpl_form, **ui_texts)
    return tmpl


# eof

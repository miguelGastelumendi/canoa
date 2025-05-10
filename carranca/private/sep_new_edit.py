"""
SEP Edition

Equipe da Canoa -- 2024
mgd 2024-10-09, 11-12
"""

# cSpell: ignore tmpl wtforms werkzeug sepsusr usrlist

from flask import render_template, request
from typing import Tuple
from os.path import splitext
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from .models import Sep, MgmtSepsUser, Schema
from .wtforms import SepEdit, SepNew

from .UserSep import UserSep
from .SepIconConfig import SepIconConfig
from ..public.ups_handler import ups_handler
from ..helpers.py_helper import now, dict_to_obj, json_to_obj
from ..helpers.types_helper import svg_content
from ..helpers.route_helper import (
    get_private_form_data,
    init_form_vars,
    get_input_text,
    login_route,
    redirect_to,
)
from ..common.app_error_assistant import ModuleErrorCode, AppStumbled
from ..helpers.ui_db_texts_helper import (
    UITextsKeys,
    add_msg_success,
    add_msg_error,
    add_msg_fatal,
)

from ..common.app_context_vars import app_user


def do_sep_edit(code: str) -> str:
    """SEP Edit Form"""

    new_sep_code = "+"
    new_sep_id = 0
    is_new = code == new_sep_code
    is_edit = not is_new
    sep_id = new_sep_id if is_new else UserSep.to_id(code)
    if sep_id is None or sep_id < 0:
        return redirect_to(login_route())

    task_code = ModuleErrorCode.SEP_EDIT.value
    tmpl_form, template, is_get, ui_texts = init_form_vars()
    sep_fullname = f"SPC&#8209;{code}"  # &#8209 is nobreak-hyphen &hyphen does not work.
    try:
        task_code += 1  # 1

        def _get_sep_data(task_code: int, load_sep_content: bool) -> Tuple[UserSep, int]:
            task_code += 1
            if is_edit:
                pass
            elif app_user.is_power:
                sep_fake = dict_to_obj({"description": "", "icon_file_name": SepIconConfig.empty_file})
                ui_texts["schemaList"] = Schema.get_schemas()
                return None, sep_fake, "", task_code + 5
            else:
                raise AppStumbled(add_msg_fatal("sepNewNotAllow", ui_texts), task_code)

            # is_edit ->
            # is it in the internal list?
            usr_sep = next((sep for sep in app_user.seps if sep.id == sep_id), None)
            if usr_sep is None:
                raise AppStumbled(add_msg_fatal("sepEditNotAllow", ui_texts), task_code)

            task_code += 1
            sep_fullname = usr_sep.fullname
            ui_texts[UITextsKeys.Form.icon_url] = usr_sep.icon_url

            # is it in the db 'permission table'?
            sep_usr_rows, _ = MgmtSepsUser.get_sepsusr_and_usrlist(app_user.id)

            if sep_usr_rows is None:
                raise AppStumbled(add_msg_fatal("sepEditNotAllow", ui_texts), task_code + 1)
            elif None == next((mus for mus in sep_usr_rows if mus.id == sep_id), None):
                raise AppStumbled(add_msg_fatal("sepEditNotAllow", ui_texts), task_code + 2)
            elif (sep_row := Sep.get_sep(sep_id, load_sep_content)[0]) is None:
                raise AppStumbled(add_msg_fatal("sepEditNotFound", ui_texts), task_code + 3)
            else:
                task_code += 4

            return usr_sep, sep_row, sep_fullname, task_code

        def _get_svg_content(file_obj: FileStorage, sep_row: Sep, task_code) -> svg_content:
            data: svg_content = ""
            _, ext = splitext(file_obj.filename)
            if not ext.lower().endswith(SepIconConfig.ext.lower()):
                task_code += 1
            elif not ((data := file_obj.read().decode("utf-8")) and len(data := data.strip()) > 30):
                task_code += 2
            elif not (data.startswith("<svg") and data.endswith("</svg>")):
                task_code += 3
            else:
                return "" if (sep_row.icon_svg or "") == (data or "") else data

            add_msg_error("sepEditInvalidFormat", ui_texts, SepIconConfig.ext)
            return None

        task_code += 1  # 2
        template, is_get, ui_texts = get_private_form_data("sepNewEdit")
        ui_texts["formForNew"] = is_new
        ui_texts["formTitle"] = ui_texts[f"formTitle{('Edit' if is_edit else 'New')}"]
        task_code += 1  # 3
        tmpl_form = SepEdit(request.form) if is_edit else SepNew(request.form)
        task_code += 1  # 4
        usr_sep, sep_row, sep_fullname, task_code = _get_sep_data(task_code, not is_get)  # 5
        task_code += 1  # 10
        file_content = None
        if is_get:
            task_code += 1  # 11
            tmpl_form.name.data = sep_fullname
            task_code += 1  # 12
            tmpl_form.description.data = sep_row.description
            tmpl_form.icon_filename.data = sep_row.icon_file_name
        else:  # is post
            task_code += 3  # 10+3= 13
            description = get_input_text(tmpl_form.description.name)
            task_code += 1  # 14
            file_obj = request.files.get(tmpl_form.icon_filename.name)
            # file_obj SHOULD by None when no file name, but not in may case (Firefox?)
            file_ready = bool(file_obj and file_obj.filename)
            task_code += 1  # 15
            if description == sep_row.description and not file_ready:  # nothing changed
                return redirect_to(login_route())
            # Note: `file_content` can be an empty string, indicating that the content is identical to the one in the database, so it should be ignored.
            elif file_ready and (file_content := _get_svg_content(file_obj, sep_row, task_code)) is None:
                pass  # go show the raised error msg
            else:
                task_code += 1  # 16
                new_icon = bool(file_content)  # can be an empty string, not a new_icon
                sep_row.description = description
                if new_icon:
                    sep_row.icon_original_name = secure_filename(file_obj.filename)
                    sep_row.icon_file_name = f"{app_user.code}u-{sep_row.id:03}sep.{SepIconConfig.ext}"
                    sep_row.icon_uploaded_at = now()
                    sep_row.icon_version = sep_row.icon_version + 1 if sep_row.icon_version > 0 else 1
                    sep_row.icon_svg = file_content

                if not Sep.set_sep(sep_row):
                    task_code += 1  # 18
                    add_msg_fatal("sepEditFailed", ui_texts, sep_fullname, task_code)
                else:
                    task_code += 2  # 19
                    add_msg_success("sepEditSuccess", ui_texts, sep_fullname)
                    if new_icon and usr_sep:  # after post
                        from .sep_icon import icon_refresh

                        icon_refresh(usr_sep)  # refresh this form icon

    except Exception as e:
        msg = add_msg_fatal("sepEditException", ui_texts, sep_fullname, task_code)
        _, template, ui_texts = ups_handler(task_code, msg, e)
        tmpl = render_template(template, **ui_texts)

    # ??  import pdb; pdb.set_trace()  # Pause here to inspect `context`
    tmpl = render_template(template, form=tmpl_form, **ui_texts)
    return tmpl


# eof

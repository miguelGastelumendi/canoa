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

from .models import Sep, MgmtSepsUser
from .wtforms import SepEdit

from .UserSep import UserSep
from .SepIconConfig import SepIconConfig
from ..public.ups_handler import ups_handler
from ..helpers.py_helper import now
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


def do_sep_edit(sep_id: int) -> str:
    """SEP Edit Form"""

    task_code = ModuleErrorCode.SEP_EDIT.value
    tmpl_form, template, is_get, ui_texts = init_form_vars()
    sep_fullname = "?"
    try:
        task_code += 1  # 1

        def _get_sep(task_code: int) -> Tuple[UserSep, int]:
            task_code += 1
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
                raise AppStumbled(add_msg_fatal("sepEditNotAllow", ui_texts), task_code)
            elif None == next((mus for mus in sep_usr_rows if mus.sep_id == sep_id), None):
                raise AppStumbled(add_msg_fatal("sepEditNotAllow", ui_texts), task_code + 1)
            elif (sep_row, sep_fullname := Sep.get_sep(sep_id)) == (None, sep_fullname):
                raise AppStumbled(add_msg_fatal("sepEditNotFound", ui_texts), task_code + 2)
            else:
                task_code += 3

            return sep_row, sep_fullname, task_code

        def _get_svg_content(file_obj: FileStorage, task_code) -> svg_content:
            data: svg_content = ""
            _, ext = splitext(file_obj.filename)
            if ext.lower().endswith(SepIconConfig.ext.lower()):
                task_code += 1
            elif (data := file_obj.read().decode("utf-8")) == None:
                task_code += 2
            elif data.startswith("<svg") and data.endswith("</svg>"):
                return data

            msg = add_msg_error("sepEditInvalidFormat", ui_texts, file_obj.filename, ext)
            raise AppStumbled(msg, task_code)

        task_code += 1  # 2
        template, is_get, ui_texts = get_private_form_data("sepEdit")
        task_code += 1  # 3
        tmpl_form = SepEdit(request.form)
        task_code += 1  # 4
        sep_row, sep_fullname, task_code = _get_sep(task_code)  # 5
        task_code += 1  # 8
        file_content = None
        if is_get:
            task_code += 1  # 7
            tmpl_form.name.data = sep_fullname
            task_code += 1  # 8
            tmpl_form.description.data = sep_row.description
            tmpl_form.icon_filename.data = sep_row.icon_file_name
        else:  # is post
            # TODO detected if form changed
            task_code += 3  # 6+3 = 9
            description = get_input_text(tmpl_form.description.name)
            task_code += 1  # 10
            file_obj = request.files[tmpl_form.icon_filename.name] if len(request.files) > 0 else None
            task_code += 1  # 11
            if description == sep_row.description and not file_obj:
                return redirect_to(login_route())
            elif file_obj and not (file_content := _get_svg_content()):
                pass  # already raised an error
            else:
                task_code += 1  # 12
                if new_icon := not (sep_row.icon_svg == file_content):
                    sep_row.icon_original_name = secure_filename(file_obj.filename)
                    sep_row.icon_file_name = f"{app_user.code}u-{sep_row.id:03}sep.{SepIconConfig.ext}"
                    sep_row.icon_uploaded_at = now()
                    sep_row.icon_version = sep_row.icon_version + 1 if sep_row.icon_version else 0
                    sep_row.icon_svg = file_content

                task_code += 1
                if not Sep.set_sep(sep_row):
                    add_msg_fatal("sepEditFailed", ui_texts, sep_fullname, task_code)
                else:
                    add_msg_success("sepEditSuccess", ui_texts, sep_fullname)
                    if new_icon:  # after post
                        from .sep_icon import icon_refresh

                        icon_refresh(app_user.seps)  # refresh this form icon

    except Exception as e:
        msg = add_msg_fatal("sepEditException", ui_texts, sep_fullname, task_code)
        _, template, ui_texts = ups_handler(task_code, msg, e)
        tmpl = render_template(template, **ui_texts)

    tmpl = render_template(template, form=tmpl_form, **ui_texts)
    return tmpl


# eof

"""
    SEP Edition

    Equipe da Canoa -- 2024
    mgd 2024-10-09
"""

# cSpell: ignore mgmt tmpl wtforms werkzeug

from os import path
from flask import render_template, request
from flask_login import current_user
from werkzeug.utils import secure_filename


from .models import MgmtSep
from .wtforms import SepEdit
from .sep_const import SCHEMA_ICON_URL, SCHEMA_ICON_LOCAL_PATH, SCHEMA_ICON_EMPTY, SCHEMA_ICON_EXTENSION

from ..Sidekick import sidekick
from ..helpers.py_helper import is_str_none_or_empty, now
from ..helpers.user_helper import get_user_code
from ..helpers.file_helper import folder_must_exist
from ..helpers.error_helper import ModuleErrorCode
from ..helpers.route_helper import get_private_form_data
from ..helpers.route_helper import init_form_vars, get_input_text
from ..helpers.ui_texts_helper import add_msg_success, add_msg_error, add_msg_fatal


# TODO  try  except, divide in to
def icon_prepare_for_form(sep: MgmtSep) -> str:
    """returns the full path of the sep icon:
    SCHEMA_ICON_EMPTY if None else
    """
    file_full_name = path.join(SCHEMA_ICON_LOCAL_PATH, sep.icon_file_name)
    url_file_name = SCHEMA_ICON_URL.format(sep.icon_file_name)
    if not folder_must_exist(SCHEMA_ICON_LOCAL_PATH):
        return ""
    elif is_str_none_or_empty(sep.icon_file_name):
        url_empty = SCHEMA_ICON_URL.format(SCHEMA_ICON_EMPTY)
        return url_empty
    elif path.isfile(file_full_name):
        # Just in case
        # with open(file_full_name, 'r', encoding='utf-8') as file:
        #     content = file.read()
        return url_file_name
    else:
        content = MgmtSep.get_sep_icon_content(sep.id)
        with open(file_full_name, "w", encoding="utf-8") as file:
            file.write(content)
        return url_file_name


def do_sep_edit() -> str:
    task_code = ModuleErrorCode.SEP_EDIT.value
    tmpl_form, template, is_get, uiTexts = init_form_vars()

    sep_fullname = "(?)"
    try:
        task_code += 1  # 1
        user = current_user

        def _get_sep() -> MgmtSep:
            try:
                sep, sep_fullname = MgmtSep.get_sep(user.mgmt_sep_id)
                icon_file = icon_prepare_for_form(sep)
                uiTexts["iconFileName"] = icon_file
                if sep is None:
                    raise (add_msg_fatal("sepEditNotFound", uiTexts))
            except Exception as e:
                raise (add_msg_fatal("sepEditSelectError", uiTexts))

            return sep, sep_fullname

        task_code += 1  # 2
        template, is_get, uiTexts = get_private_form_data("sepEdit")
        task_code += 1  # 3
        tmpl_form = SepEdit(request.form)
        if user.mgmt_sep_id is None:
            add_msg_fatal("sepEditNotFound", uiTexts)
        elif is_get:
            task_code += 1  # 4
            sep, sep_fullname = _get_sep()
            task_code += 1  # 5
            tmpl_form.name.data = sep_fullname
            task_code += 1  # 6
            tmpl_form.description.data = sep.description
        else:  # is post
            task_code += 5  # 8
            sep, sep_fullname = _get_sep()
            task_code += 1  # 9
            sep.description = get_input_text(tmpl_form.description.name)
            task_code += 1  # 10
            file_obj = request.files[tmpl_form.icon_filename.name] if len(request.files) > 0 else None

            task_code += 1  # 11
            if not file_obj:
                pass  # and save
            elif file_obj.filename.lower().endswith(SCHEMA_ICON_EXTENSION.lower()):
                task_code += 1  # 12
                sep.icon_original_name = secure_filename(file_obj.filename)
                task_code += 1  # 13
                sep.icon_file_name = f"{get_user_code(user.id)}u-{sep.id:03}di.{SCHEMA_ICON_EXTENSION}"
                sep.icon_uploaded_at = now()
                task_code += 1  # 14
                sep.icon_svg = file_obj.read().decode("utf-8")
            else:
                task_code += 1  # 12
                msg = add_msg_error(
                    "sepEditInvalidFormat", uiTexts, file_obj.filename, SCHEMA_ICON_EXTENSION.upper()
                )
                raise Exception(msg)

            task_code += 5  # 1
            if MgmtSep.set_sep(sep):
                add_msg_success("sepEditSuccess", uiTexts, sep_fullname)
            else:
                add_msg_fatal("sepEditFailed", uiTexts, sep_fullname, task_code)

    except Exception as e:
        msg = add_msg_fatal("sepEditException", uiTexts, sep_fullname, task_code)
        sidekick.display.error(msg)
        sidekick.app_log.error(e)

    tmpl = render_template(template, form=tmpl_form, **uiTexts)
    return tmpl


# eof

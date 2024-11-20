"""
    SEP Edition

    Equipe da Canoa -- 2024
    mgd 2024-10-09
"""

# cSpell: ignore mgmt tmpl wtforms werkzeug
from typing import Tuple, Any

from flask import render_template, request
from flask_login import current_user
from werkzeug.utils import secure_filename


from .models import MgmtSep
from .wtforms import SepEdit

from ..Sidekick import sidekick
from ..helpers.py_helper import now
from ..helpers.user_helper import get_user_code
from ..helpers.error_helper import ModuleErrorCode
from ..helpers.route_helper import get_private_form_data
from ..helpers.route_helper import init_form_vars, get_input_text
from ..helpers.ui_texts_helper import ui_msg_info, add_msg_success, add_msg_error, add_msg_fatal

from .SepIconConfig import SepIconConfig


def do_sep_edit() -> str:
    """SEP Edit Form"""

    task_code = ModuleErrorCode.SEP_EDIT.value
    tmpl_form, template, is_get, uiTexts = init_form_vars()

    sep_fullname = "(preparando...)"
    try:
        task_code += 1  # 1
        user = current_user

        def _get_sep(task_code: int) -> Tuple[MgmtSep, str, int]:
            from .sep_icon import icon_prepare_for_html

            try:
                sep, sep_fullname = MgmtSep.get_sep(user.mgmt_sep_id)
                if sep is None or user.mgmt_sep_id is None:
                    raise add_msg_fatal("sepEditNotFound", uiTexts)
                task_code += 1  #
                url_file_name, _ = icon_prepare_for_html(sep)
                uiTexts["iconFileName"] = url_file_name
                uiTexts[ui_msg_info] = uiTexts[ui_msg_info].format(sep_fullname)
            except Exception as e:
                raise (add_msg_fatal("sepEditSelectError", uiTexts))

            return sep, sep_fullname, task_code

        task_code += 1  # 2
        template, is_get, uiTexts = get_private_form_data("sepEdit")
        task_code += 1  # 3
        tmpl_form = SepEdit(request.form)
        task_code += 1  # 4
        sep, sep_fullname, task_code = _get_sep(task_code)  # 5
        task_code += 1  # 6
        if is_get:
            task_code += 1  # 7
            tmpl_form.name.data = sep_fullname
            task_code += 1  # 8
            tmpl_form.description.data = sep.description
            tmpl_form.icon_filename.data = sep.icon_file_name
        else:  # is post
            task_code += 3  # 6+3 = 9
            sep.description = get_input_text(tmpl_form.description.name)
            task_code += 1  # 10
            file_obj = request.files[tmpl_form.icon_filename.name] if len(request.files) > 0 else None
            task_code += 1  # 11
            if not file_obj:
                pass  # and save
            elif file_obj.filename.lower().endswith(SepIconConfig.ext.lower()):
                task_code += 1  # 12
                sep.icon_original_name = secure_filename(file_obj.filename)
                task_code += 1  # 13
                sep.icon_file_name = f"{get_user_code(user.id)}u-{sep.id:03}sep.{SepIconConfig.ext}"
                sep.icon_uploaded_at = now()
                task_code += 1  # 14
                sep.icon_svg = file_obj.read().decode("utf-8")
            else:
                task_code += 5  # 11+5 = 16
                msg = add_msg_error(
                    "sepEditInvalidFormat", uiTexts, file_obj.filename, SepIconConfig.ext.upper()
                )
                raise Exception(msg)

            task_code = 17
            if MgmtSep.set_sep(sep):
                add_msg_success("sepEditSuccess", uiTexts, sep_fullname)
            else:
                add_msg_fatal("sepEditFailed", uiTexts, sep_fullname, task_code)

    except Exception as e:
        # Aqui
        msg = add_msg_fatal("sepEditException", uiTexts, sep_fullname, task_code)
        sidekick.display.error(msg)
        sidekick.app_log.error(e)

    tmpl = render_template(template, form=tmpl_form, **uiTexts)
    return tmpl


# eof

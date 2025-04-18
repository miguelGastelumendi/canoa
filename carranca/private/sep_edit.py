"""
SEP Edition

Equipe da Canoa -- 2024
mgd 2024-10-09, 11-12
"""

# cSpell: ignore mgmt tmpl wtforms werkzeug

from flask import render_template, request
from typing import Tuple
from werkzeug.utils import secure_filename

from .models import MgmtSep
from .wtforms import SepEdit

from ..helpers.py_helper import now
from ..helpers.route_helper import get_private_form_data
from ..helpers.route_helper import init_form_vars, get_input_text
from ..common.app_error_assistant import ModuleErrorCode, CanoeStumbled, did_I_stumbled
from ..helpers.ui_db_texts_helper import (
    UITextsKeys,
    add_msg_success,
    add_msg_error,
    add_msg_fatal,
)
from ..common.app_context_vars import logged_user


def do_sep_edit() -> str:
    """SEP Edit Form"""

    from .SepIconConfig import SepIconConfig

    task_code = ModuleErrorCode.SEP_EDIT.value
    tmpl_form, template, is_get, ui_texts = init_form_vars()

    sep_fullname = "" if logged_user.sep is None else logged_user.sep.full_name
    try:
        task_code += 1  # 1

        def _get_sep(task_code: int) -> Tuple[MgmtSep, str, int]:
            try:
                sep, sep_fullname = MgmtSep.get_sep(logged_user.sep.id)
                if sep is None or logged_user.sep.id is None:
                    raise CanoeStumbled(add_msg_fatal("sepEditNotFound", ui_texts), task_code)
                task_code += 1  #
                ui_texts[UITextsKeys.Form.icon_url] = logged_user.sep.icon_url
                ui_texts[UITextsKeys.Msg.info] = ui_texts[UITextsKeys.Msg.info].format(sep_fullname)
            except CanoeStumbled:
                raise
            except Exception:
                raise CanoeStumbled(add_msg_fatal("sepEditSelectError", ui_texts), task_code)

            return sep, sep_fullname, task_code

        task_code += 1  # 2
        template, is_get, ui_texts = get_private_form_data("sepEdit")
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
            # TODO detected if form changed
            new_icon = False
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
                sep.icon_file_name = f"{logged_user.code}u-{sep.id:03}sep.{SepIconConfig.ext}"
                sep.icon_uploaded_at = now()
                task_code += 1  # 14
                sep.icon_svg = file_obj.read().decode("utf-8")
                task_code += 1  # 15
                new_icon = True
            else:
                task_code += 7  # 11+7 = 18
                ext = SepIconConfig.ext.upper()
                msg = add_msg_error("sepEditInvalidFormat", ui_texts, file_obj.filename, ext)
                raise CanoeStumbled(msg, task_code)

            task_code += 19
            if not MgmtSep.set_sep(sep):
                add_msg_fatal("sepEditFailed", ui_texts, sep_fullname, task_code)
            else:
                add_msg_success("sepEditSuccess", ui_texts, sep_fullname)
                if new_icon:  # after post
                    from .sep_icon import icon_refresh

                    icon_refresh(logged_user.sep)  # refresh this form icon

    except Exception as e:
        from ..common.app_context_vars import sidekick

        msg = (
            str(e)
            if did_I_stumbled(e)
            else add_msg_fatal("sepEditException", ui_texts, sep_fullname, task_code)
        )
        sidekick.display.error(msg)
        sidekick.app_log.error(e)

    tmpl = render_template(template, form=tmpl_form, **ui_texts)
    return tmpl


# eof

"""
    Initialize the upload file process

    Part of Canoa `File Validation` Processes
    Equipe da Canoa -- 2024
    mgd
"""

# cSpell: ignore werkzeug wtforms uploadfile tmpl urlname

from flask import render_template, request

from .wtforms import UploadFileForm
from ..shared import app_log
from ..helpers.py_helper import is_str_none_or_empty
from ..helpers.user_helper import LoggedUser, get_user_receipt
from ..helpers.texts_helper import add_msg_success, add_msg_error
from ..helpers.route_helper import get_private_form_data, get_input_text
from ..helpers.dwnLd_goo_helper import is_gd_url_valid


def upload_file() -> str:
    template, is_get, texts = get_private_form_data("uploadfile")
    tmpl_form = UploadFileForm(request.form)

    if not is_get:

        def _log_error(msg_id: str, code: int) -> str:
            log_error = add_msg_error(msg_id, texts, code)
            app_log.error(log_error, exc_info=code)

        ve = texts["validExtensions"]
        valid_extensions = ".zip" if is_str_none_or_empty(ve) else ve.lower().split(",")
        logged_user = LoggedUser()
        file_obj = request.files[tmpl_form.filename.id] if request.files else None
        url_str = get_input_text(tmpl_form.urlname.name)

        has_file = (file_obj != None) and not is_str_none_or_empty(file_obj.filename)
        has_url = not is_str_none_or_empty(url_str)
        file_data = url_str if has_url else file_obj
        task_code = 1
        if has_file and has_url:
            _log_error("uploadFileCheck_both", task_code + 1)
        elif not (has_file or has_url):
            _log_error("uploadFileCheck_none", task_code + 2)
        elif has_url and (is_gd_url_valid(url_str) > 0):
            _log_error("uploadFileCheck_bad_url", task_code + 3)
        else:
            from .upload_files.process import process

            error_code, msg_error, _, data = process(
                logged_user, file_data, valid_extensions
            )
            if error_code == 0:
                file_ticket = data.get("file_ticket")
                user_receipt = get_user_receipt(file_ticket)
                log_msg = add_msg_success(
                    "uploadFileSuccess", texts, user_receipt, logged_user.email
                )
                app_log.debug(log_msg)
            else:
                _log_error(msg_error, error_code)
                # app_log.debug(f"Uploadfile: {log_msg} | File stage '{_file}' |{removed} Code {error_code} | Exception Error '{msg_error}'.")

    return render_template(template, form=tmpl_form, **texts)


# eof

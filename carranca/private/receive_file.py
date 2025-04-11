"""
Initialize the receive file process

Part of Canoa `File Validation` Processes
Equipe da Canoa -- 2024
mgd
"""

# cSpell: ignore werkzeug wtforms tmpl urlname mgmt

from flask import render_template, request
from werkzeug.utils import secure_filename

from ..common.app_context_vars import sidekick, logged_user
from ..config.ValidateProcessConfig import ValidateProcessConfig

from ..helpers.py_helper import is_str_none_or_empty
from ..helpers.file_helper import folder_must_exist
from ..helpers.user_helper import now
from ..common.app_error_assistant import ModuleErrorCode
from ..helpers.route_helper import get_private_form_data, get_input_text
from ..helpers.ui_db_texts_helper import (
    UITextsKeys,
    add_msg_success,
    add_msg_error,
    add_msg_fatal,
)
from ..helpers.dwnLd_goo_helper import is_gd_url_valid, download_public_google_file

from .wtforms import ReceiveFileForm

from .validate_process.ProcessData import ProcessData

RECEIVE_FILE_DEFAULT_ERROR: str = "uploadFileError"

# link em gd de test em mgd account https://drive.google.com/file/d/1yn1fAkCQ4Eg1dv0jeV73U6-KETUKVI58/view?usp=sharing


def receive_file() -> str:
    template, is_get, ui_texts = get_private_form_data("receiveFile")
    tmpl_form = ReceiveFileForm(request.form)

    def _result():
        ui_texts[UITextsKeys.Form.icon] = None if logged_user.sep is None else logged_user.sep.icon_url
        tmpl = render_template(template, form=tmpl_form, **ui_texts)
        return tmpl

    if is_get:
        sep_fullname = ui_texts["noSEassigned"] if logged_user.sep is None else logged_user.sep.full_name
        ui_texts[UITextsKeys.Msg.info] = ui_texts[UITextsKeys.Msg.info].format(sep_fullname)
        return _result()

    def _log_error(msg_id: str, code: int, msg: str = "", fatal: bool = False) -> int:
        e_code = ModuleErrorCode.RECEIVE_FILE_ADMIT.value + code

        log_error = (
            add_msg_fatal(msg_id, ui_texts, e_code, msg)
            if fatal
            else add_msg_error(msg_id, ui_texts, e_code, msg)
        )
        sidekick.app_log.error(log_error)
        return e_code

    try:
        task_code = 1
        error_code = 0

        received_at = now()
        # Find out what was kind of data was sent: an uploaded file or an URL (download)
        file_obj = request.files[tmpl_form.filename.id] if len(request.files) > 0 else None
        task_code += 1  # 2
        url_str = get_input_text(tmpl_form.urlname.name)
        task_code += 1  # 3
        has_file = (file_obj is not None) and not is_str_none_or_empty(file_obj.filename)
        task_code += 1  # 4
        has_url = not is_str_none_or_empty(url_str)

        # file_data holds a 'str' or an 'obj'
        task_code += 1  # 5
        file_data = url_str if has_url else file_obj

        # Basic check, both, none or bad url
        if has_file and has_url:
            error_code = _log_error("receiveFileAdmit_both", task_code + 1)  # 6
            return _result()
        elif not (has_file or has_url):
            error_code = _log_error("receiveFileAdmit_none", task_code + 2)  # 7
            return _result()
        elif has_url and is_gd_url_valid(url_str) > 0:
            error_code = _log_error("receiveFileAdmit_bad_url", task_code + 3)  # 8
            return _result()

        # Instantiate Process Data helper
        task_code = 10

        def doProcessData() -> tuple[bool, ProcessData]:
            receive_file_cfg = ValidateProcessConfig(sidekick.debugging)
            common_folder = sidekick.config.COMMON_PATH
            pd = ProcessData(
                logged_user.code,
                logged_user.folder,
                common_folder,
                receive_file_cfg.dv_app.folder,
                receive_file_cfg.dv_app.batch,
                has_url,
            )
            return receive_file_cfg.debug_process, pd

        task_code += 1  # 11
        debug_process, pd = doProcessData()
        if has_file:
            task_code += 1  # 12
            pd.received_original_name = file_obj.filename
            # TODO check file_obj. file_obj.mimetype file_obj.content_length
        elif not folder_must_exist(pd.path.working_folder):
            task_code += 2  # 13
            error_code = _log_error(RECEIVE_FILE_DEFAULT_ERROR, task_code)
            return _result()
        else:
            task_code += 3  # 14
            # this is a placeholder for the real name (I yet don't know it)
            # so pd.working_file_name() has the correct format to
            pd.received_file_name = "{0}"
            download_code, filename, md = download_public_google_file(
                url_str,
                pd.path.working_folder,
                pd.working_file_name(),
                True,
                debug_process,
            )
            if download_code == 0:
                task_code += 1  # 15
                pd.received_original_name = md["name"]
            else:
                sidekick.app_log.error(f"Download error code {download_code}.")
                fn = filename if filename else "<ainda sem nome>"
                task_code += 2  # 16
                error_code = _log_error("receiveFileAdmit_bad_dl", task_code, fn)
                return _result()

        pd.received_file_name = secure_filename(pd.received_original_name)
        task_code = 20  # 20
        ve = ui_texts["validExtensions"]
        valid_extensions = ".zip" if is_str_none_or_empty(ve) else ve.lower().split(",")

        task_code += 1  # 21
        from .validate_process.process import process

        task_code += 1  # 22
        error_code, msg_error, _ = process(logged_user, file_data, pd, received_at, valid_extensions)

        if error_code == 0:
            log_msg = add_msg_success("uploadFileSuccess", ui_texts, pd.user_receipt, logged_user.email)
            sidekick.display.debug(log_msg)
        else:
            log_msg = _log_error(msg_error, error_code, "", True)
            sidekick.display.error(log_msg)

    except Exception as e:
        e_code = _log_error(RECEIVE_FILE_DEFAULT_ERROR, task_code, "", True)
        sidekick.app_log.fatal(f"{RECEIVE_FILE_DEFAULT_ERROR}: Code {e_code}, Message: {e}.")

    tmpl = _result()
    return tmpl


# eof

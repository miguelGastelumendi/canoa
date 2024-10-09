"""
    Initialize the receive file process

    Part of Canoa `File Validation` Processes
    Equipe da Canoa -- 2024
    mgd
"""

# cSpell: ignore werkzeug wtforms tmpl urlname receivefile

from flask import render_template, request

from .wtforms import ReceiveFileForm
from werkzeug.utils import secure_filename
from .validate_process.ProcessData import ProcessData

from ..main import shared
from ..helpers.py_helper import is_str_none_or_empty
from ..helpers.file_helper import path_remove_last_folder, folder_must_exist
from ..helpers.user_helper import LoggedUser, now
from ..helpers.error_helper import ModuleErrorCode
from ..helpers.route_helper import get_private_form_data, get_input_text
from ..helpers.ui_texts_helper import add_msg_success, add_msg_error
from ..helpers.dwnLd_goo_helper import is_gd_url_valid, download_public_google_file
from ..config_validate_process import ValidateProcessConfig

RECEIVE_FILE_DEFAULT_ERROR = "uploadFileError"

# link em gd de test em mgd account https://drive.google.com/file/d/1yn1fAkCQ4Eg1dv0jeV73U6-KETUKVI58/view?usp=sharing


def receive_file() -> str:
    template, is_get, texts = get_private_form_data("receiveFile")
    tmpl_form = ReceiveFileForm(request.form)

    def _result():
        return render_template(template, form=tmpl_form, **texts)

    if is_get:
        return _result()

    def _log_error(msg_id: str, code: int, msg: str = "") -> int:
        error_code = ModuleErrorCode.RECEIVE_FILE_ADMIT + code
        log_error = add_msg_error(msg_id, texts, error_code, msg)
        shared.app_log.error(log_error, exc_info=error_code)
        return error_code

    try:
        received_at = now()
        # Find out what was kind of data was sent: an uploaded file or an URL (download)
        file_obj = request.files[tmpl_form.filename.id] if request.files else None
        url_str = get_input_text(tmpl_form.urlname.name)
        has_file = (file_obj is not None) and not is_str_none_or_empty(file_obj.filename)
        has_url = not is_str_none_or_empty(url_str)

        # file_data holds a 'str' or an 'obj'
        file_data = url_str if has_url else file_obj

        # Basic check, both, none or bad url
        task_code = 1
        error_code = 0

        if has_file and has_url:
            error_code = _log_error("receiveFileAdmit_both", task_code + 1)
            return _result()
        elif not (has_file or has_url):
            error_code = _log_error("receiveFileAdmit_none", task_code + 2)
            return _result()
        elif has_url and is_gd_url_valid(url_str) > 0:
            error_code = _log_error("receiveFileAdmit_bad_url", task_code + 3)
            return _result()

        # Instantiate Process Data helper
        task_code = 5
        logged_user = LoggedUser()

        def doProcessData() -> tuple[bool, ProcessData]:
            receive_file_cfg = ValidateProcessConfig(shared.app_config.APP_DEBUG)
            common_folder = path_remove_last_folder(shared.app_config.ROOT_FOLDER)
            pd = ProcessData(
                logged_user.code,
                logged_user.folder,
                common_folder,
                receive_file_cfg.d_v.folder,
                receive_file_cfg.d_v.batch,
                has_url,
            )
            return receive_file_cfg.debug_process, pd

        task_code += 1  # 6
        debug_process, pd = doProcessData()
        if has_file:
            task_code += 1  # 7
            pd.received_original_name = file_obj.filename
            # TODO check file_obj. file_obj.mimetype file_obj.content_length
        elif not folder_must_exist(pd.path.working_folder):
            task_code += 2  # 8
            error_code = _log_error(RECEIVE_FILE_DEFAULT_ERROR, task_code)
            return _result()
        else:
            task_code += 3  # 9
            # this is a placeholder for the real name (I yet don't know it)
            # so si.working_file_name() has the correct format to
            pd.received_file_name = "{0}"
            download_code, filename, md = download_public_google_file(
                url_str,
                pd.path.working_folder,
                pd.working_file_name(),
                True,
                debug_process,
            )
            if download_code == 0:
                task_code += 1  # 10
                pd.received_original_name = md["name"]
            else:
                shared.app_log.error(
                    f"Download error code {download_code}.", exc_info=download_code
                )
                fn = filename if filename else "<ainda sem nome>"
                task_code += 2  # 11
                error_code = _log_error("receiveFileAdmit_bad_dl", task_code, fn)
                return _result()

        pd.received_file_name = secure_filename(pd.received_original_name)
        task_code += 1
        ve = texts["validExtensions"]
        valid_extensions = ".zip" if is_str_none_or_empty(ve) else ve.lower().split(",")

        task_code += 1
        from .validate_process.process import process

        task_code += 1
        error_code, msg_error, _, data = process(
            logged_user, file_data, pd, received_at, valid_extensions
        )

        if error_code == 0:
            log_msg = add_msg_success(
                "uploadFileSuccess", texts, pd.user_receipt, logged_user.email
            )
            shared.app_log.debug(log_msg)
        else:
            _log_error(msg_error, error_code)
            ##g.app_log.debug(f"{log_msg} | File stage '{_file}' |{removed} Code {error_code} | Exception Error '{msg_error}'.")

    except Exception as e:
        error_code = _log_error(RECEIVE_FILE_DEFAULT_ERROR, task_code)
        shared.app_log.fatal(f"{RECEIVE_FILE_DEFAULT_ERROR}: Code {error_code}, Message: {e}.")

    return _result()

# eof
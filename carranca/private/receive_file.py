"""
    Initialize the receive file process

    Part of Canoa `File Validation` Processes
    Equipe da Canoa -- 2024
    mgd
"""

# cSpell: ignore werkzeug wtforms tmpl urlname receivefile

from flask import render_template, request


from .wtforms import ReceiveFileForm
from .upload_files.StorageInfo import StorageInfo

from ..shared import app_log, app_config
from ..helpers.py_helper import is_str_none_or_empty
from ..helpers.file_helper import path_remove_last_folder, folder_must_exist
from ..helpers.user_helper import LoggedUser, get_user_receipt
from ..helpers.error_helper import ModuleErrorCode
from ..helpers.texts_helper import add_msg_success, add_msg_error
from ..helpers.route_helper import get_private_form_data, get_input_text
from ..helpers.dwnLd_goo_helper import is_gd_url_valid, download_public_google_file
from ..config_receive_file import ReceiveFileConfig

RECEIVE_FILE_DEFAULT_ERROR = "uploadFileError"


def receive_file() -> str:
    template, is_get, texts = get_private_form_data("receivefile")
    tmpl_form = ReceiveFileForm(request.form)

    def _result():
        return render_template(template, form=tmpl_form, **texts)

    if is_get:
        return _result()

    def _log_error(msg_id: str, code: int, msg: str = "") -> str:
        error_code = ModuleErrorCode.RECEIVE_FILE_ADMIT + code
        log_error = add_msg_error(msg_id, texts, error_code, msg)
        app_log.error(log_error, exc_info=error_code)
        return error_code

    try:
        # Find out what was kind of data was sent: an uploaded file or an URL (download)
        file_obj = request.files[tmpl_form.filename.id] if request.files else None
        url_str = get_input_text(tmpl_form.urlname.name)
        has_file = (file_obj != None) and not is_str_none_or_empty(file_obj.filename)
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

        # Instantiate storage helper for the process StorageInfo
        task_code = 5
        logged_user = LoggedUser()

        def do_storage() -> tuple[bool, StorageInfo]:
            receive_file_cfg = ReceiveFileConfig(app_config.DEBUG)
            common_folder = path_remove_last_folder(app_config.ROOT_FOLDER)
            si = StorageInfo(
                logged_user.code,
                common_folder,
                receive_file_cfg.d_v.folder,
                receive_file_cfg.d_v.batch,
                has_url,
            )
            return receive_file_cfg.debug_process, si

        task_code += 1
        debug_process, storage = do_storage()
        if has_file:
            task_code += 1
            storage.received_original_name = file_obj.filename
        elif not folder_must_exist(storage.path.working_folder):
            task_code += 2
            error_code = _log_error(RECEIVE_FILE_DEFAULT_ERROR, task_code)
            return _result()
        else:
            task_code += 3
            download_code, filename, _ = download_public_google_file(
                url_str, storage.path.working_folder, True, debug_process
            )
            if download_code == 0:
                task_code += 1
                storage.received_original_name = filename
            else:
                fn = filename if filename else "<ainda sem nome>"
                error_code = _log_error("receiveFileAdmit_bad_dl", task_code + 2, fn)
                return _result()

        task_code += 1
        ve = texts["validExtensions"]
        valid_extensions = ".zip" if is_str_none_or_empty(ve) else ve.lower().split(",")

        from .upload_files.process import process

        error_code, msg_error, _, data = process(
            logged_user, file_data, storage, valid_extensions
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
            ##app_log.debug(f"{log_msg} | File stage '{_file}' |{removed} Code {error_code} | Exception Error '{msg_error}'.")

    except Exception as e:
        error_code = _log_error(RECEIVE_FILE_DEFAULT_ERROR, task_code)
        app_log.error(f"{RECEIVE_FILE_DEFAULT_ERROR}: Code {error_code}, Message: {e}.")

    return _result()


# eof

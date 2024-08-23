"""
    First step:
    - Simple file validations
    - Check if exist or create process folders

    Part of Canoa `File Validation` Processes

    Equipe da Canoa -- 2024
    mgd
"""

# cSpell:ignore werkzeug ext

from os import path
from werkzeug.utils import secure_filename

from ...shared import app_log
from ...helpers.error_helper import ModuleErrorCode
from ...helpers.py_helper import is_str_none_or_empty
from ...helpers.db_helper import get_str_field_length
from ...helpers.file_helper import file_must_exist, folder_must_exist, is_same_file_name

from ..models import UserDataFiles
from .Cargo import Cargo


def check(cargo: Cargo, file_obj: object, valid_ext: list[str]) -> Cargo:

    error_code = 0
    msg_exception = ""
    task_code = 0


    try:
        cargo.storage.uploaded_file_name = (
            None if file_obj is None else secure_filename(file_obj.filename)
        )
        file_name_max_len = get_str_field_length(UserDataFiles, "file_name")

        if file_obj is None:
            task_code = 1
        elif is_str_none_or_empty(cargo.user.email):
            task_code = 2
        elif is_str_none_or_empty(cargo.storage.uploaded_file_name):
            task_code = 3
        elif is_str_none_or_empty(cargo.upload_cfg.output_file.name):
            task_code = 4
        elif is_str_none_or_empty(cargo.upload_cfg.output_file.ext):
            task_code = 5
        # usar o secure name 2024-07-30 (zap 2024-07-30)
        # elif not is_same_file_name(file_obj.filename, cargo.storage.uploaded_file_name):
        #     # invalid name, be careful
        #     task_code = 6
        elif len(cargo.storage.uploaded_file_name) > file_name_max_len:
            task_code = 7
        elif not any(
            cargo.storage.uploaded_file_name.lower().endswith(ext.strip().lower())
            for ext in valid_ext
        ):
            task_code = 8
        # elif not response.headers.get('Content-Type') == ct in valid_content_types.split(',')): #check if really zip
        # task_code = 10
        elif not folder_must_exist(cargo.storage.path.user):
            task_code = 11
        elif not folder_must_exist(cargo.storage.path.data_tunnel_user_read):
            task_code = 12
        elif not folder_must_exist(cargo.storage.path.data_tunnel_user_write):
            task_code = 13
        elif not path.isfile(cargo.storage.path.batch_source_name):
            task_code = 14
        elif not file_must_exist(
            cargo.storage.path.batch_full_name,
            cargo.storage.path.batch_source_name,
            True,
        ):
            task_code = 15
        else:
            task_code = 0


        if task_code == 0:
            if not is_same_file_name(file_obj.filename, cargo.storage.uploaded_file_name ):
                cargo.storage.uploaded_original_name = file_obj.filename
                app_log.info(f"The uploaded file [{file_obj.filename}] has been renamed to [{cargo.storage.uploaded_file_name}].")
            app_log.debug(f"The uploaded file [{cargo.storage.uploaded_file_name}] successfully passed the `check` module.")
        else:
            app_log.error(f"The uploaded file [{cargo.storage.uploaded_file_name}] failed in module `check` with code {task_code}.")

    except Exception as e:
        msg_exception = str(e)
        # is the highest possible (see ModuleErrorCode.UPLOAD_FILE_CHECK + 1)
        task_code = 19
        app_log.error(f"Exception [{e}], code {task_code}, occurred in module `check` while validating the uploaded file [{cargo.storage.uploaded_file_name}].")

    # goto module register.py
    error_code = 0 if task_code == 0 else ModuleErrorCode.UPLOAD_FILE_CHECK + task_code
    return cargo.update(error_code, "", msg_exception, {"file_obj": file_obj})


# eof

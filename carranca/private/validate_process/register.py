"""
    Second step:
    - Save the file with a unique name in Uploaded_file
    - Create a record in table user_data_files (UserDataFiles)

    Part of Canoa `File Validation` Processes

    Equipe da Canoa -- 2024
    mgd
"""

# cSpell:ignore ccitt

import os
from zlib import crc32

from ...shared import app_log
from ...helpers.py_helper import OS_IS_WINDOWS
from ...helpers.user_helper import now
from ...helpers.error_helper import ModuleErrorCode
from ..models import UserDataFiles

from .Cargo import Cargo


def register(cargo: Cargo, file_data: object | str) -> Cargo:

    def _save_uploaded_file_locally(
        full_name: str, file_obj: object
    ) -> tuple[int, int]:
        """saves on local disk the uploaded file"""
        # create the uploaded_file, from file_obj
        with open(full_name, "wb") as file:
            bytes = file_obj.read()
            file_crc32 = crc32(bytes)
            file_size = file.write(bytes)
        return file_size, file_crc32

    def _crc_from_downloaded_file(full_name: str) -> tuple[int, int]:
        file_size = os.path.getsize(full_name)
        file_crc32 = 0
        with open(full_name, "rb") as file:
            file_crc32 = crc32(file.read())
        return file_size, file_crc32

    error_code = 0
    task_code = 0
    msg_exception = ""
    file_saved = cargo.pd.file_was_downloaded
    file_registered = False
    work_fname = cargo.pd.working_file_full_name()
    try:
        register_started_at = now()
        file_size = 0
        file_crc32 = 0
        if cargo.pd.file_was_uploaded:
            file_size, file_crc32 = _save_uploaded_file_locally(work_fname, file_data)
            file_saved = True
        else:
            file_size, file_crc32 = _crc_from_downloaded_file(work_fname)

        task_code += 1  # +4
        user_dataFiles_key = cargo.pd.file_ticket
        UserDataFiles.insert( user_dataFiles_key,
            app_version = cargo.app_version,
            process_version = cargo.process_version,
            id_users=cargo.user.id,
            file_size=file_size,
            file_crc32=file_crc32,
            file_name=cargo.pd.received_file_name,
            original_name=cargo.pd.received_original_name,
            user_receipt= cargo.pd.user_receipt,
            a_received_at=cargo.received_at,
            b_process_started_at=cargo.process_started_at,
            c_check_started_at=cargo.check_started_at,
            d_register_started_at=register_started_at,
            from_os="W" if OS_IS_WINDOWS else "L", # Linux
            file_origin= "L" if cargo.pd.file_was_uploaded else "C", # Local | Cloud
        )
        task_code += 1  # +5
        file_registered= cargo.file_registered(user_dataFiles_key)
        task_code = 0  # very important!
        app_log.debug(f"The file was successfully registered in the database.")
    except Exception as e:
        task_code += 10
        msg_exception = str(e)
        msg_fatal = f"Error registering the file [{cargo.pd.received_file_name}]"
        msg_deleted = ""
        if file_saved and not file_registered:
            os.remove(work_fname)
            msg_deleted = " (so it was locally deleted)"
        app_log.fatal(f"{msg_fatal}{msg_deleted}. Error: [{msg_exception}].")

    # goto module unzip
    error_code = (
        0 if task_code == 0 else ModuleErrorCode.RECEIVE_FILE_REGISTER + task_code
    )
    return cargo.update(error_code, "", msg_exception, {}, {})


# eof

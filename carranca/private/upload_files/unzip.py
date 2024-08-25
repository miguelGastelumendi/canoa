"""
    Third step:
    - Unzip the uploaded file to a common folder with `data_validate` app

    Part of Canoa `File Validation` Processes

    Equipe da Canoa -- 2024
    mgd
"""
# cSpell:ignore

import zipfile
from .Cargo import Cargo
from ...shared import app_log
from ...helpers.user_helper import  now
from ...helpers.error_helper import ModuleErrorCode

def unzip(cargo: Cargo) -> Cargo:
    """
    Check the uploaded file as a zip,
    unzip it into the data_tunnel shared folder
    with `data_validate` app
    """

    msg_error = ''
    error_code = 0
    msg_exception = ''
    task_code = 0

    cargo.unzip_started_at = now()
    zip_full_name = cargo.si.working_file_full_name()
    unzip_folder = cargo.si.path.data_tunnel_user_write

    try:
        task_code = 1
        msg_error = "uploadFileZip_unknown"
        with zipfile.ZipFile(zip_full_name, 'r') as zip_file:
            if zip_file.testzip() is not None:
                task_code = 2
                msg_error = "uploadFileZip_corrupted"
                raise RuntimeError(msg_error)
            else:
                task_code = 3
                msg_error = "uploadFileZip_extraction_error"
                zip_file.extractall(unzip_folder)
                msg_error = ''

        app_log.debug(f"The zip file [{zip_full_name}] was unpacked correctly in [{unzip_folder}].")
    except Exception as e:
        msg_exception= str(e)
        error_code= task_code + ModuleErrorCode.RECEIVE_FILE_UNZIP
        app_log.error(f"Error unzipping file [{zip_full_name}] in [{unzip_folder}]: [{e}].", exc_info=error_code)


    # goto module submit.py
    return cargo.update(error_code, msg_error, msg_exception)

# eof

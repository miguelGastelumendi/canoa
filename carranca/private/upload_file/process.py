# Equipe da Canoa -- 2024
#
# mgd
# cSpell:ignore ext
"""
Performs the complete validation process:
    - Check: file name, create folders
    - Register

Part of Canoa `File Validation` Processes
"""

from ..models import UserDataFiles
from ...helpers.user_helper import LoggedUser
from ...helpers.py_helper import is_str_none_or_empty, path_remove_last
from ...helpers.error_helper import ModuleErrorCode

from .Cargo import Cargo
from .StorageInfo import StorageInfo
from .check import check
from .unzip import unzip
from .register import register
from .submit import submit
from .email import email


def process(logged_user: LoggedUser, file_obj: object, valid_ext: list[str]) -> list[int, str, str]:
    from main import app_config
    proc_name = __name__.split('.')[-1]

    def __get_params(cargo: Cargo) -> list[object, dict]:
        """
        Extracts the parameters of the next procedure,
        initialize cargo and returns to the loop
        """
        params = dict(cargo.next)
        return cargo.init(), params

    def __get_msg_exception(e_str: str, msg_exc: str,  code: int) -> str:
        """ prepares a complete exception message for the db & log """
        return f"Upload Error: process.Exception: [{e_str}]; {proc_name}.Exception: [{msg_exc}], Code [{code}]."


    # Parent folder of both apps: canoa & data_validate
    common_folder = path_remove_last(app_config.ROOT_FOLDER)

    # output file of the data_validate app
    data_validate = {
         'file_name' : app_config.data_validate_file_name,
         'file_ext': app_config.data_validate_file_ext,
    }

    # Create the Storage Info
    storage = StorageInfo(logged_user.code, common_folder, data_validate)

    # Create Cargo, with the parameters for the first procedure (check) of the Loop Process
    cargo = Cargo(logged_user, storage, {'file_obj': file_obj, 'valid_ext': valid_ext})
    error_code = 0
    msg_error = ''
    msg_exception = ''


    """
        Process Loop
        runs all the necessary steps (modules) to generate the final `report` and send it by email.

        `proc` Template:
        def proc(cargo: Cargo, param1, param2, ...) -> cargo.:
          ''' process ....
    """
    for proc in [check, register, unzip, submit, email]:
        proc_name = proc.__name__
        try:
            cargo, params = __get_params(cargo)
            error_code, msg_error, msg_exception, cargo = proc(cargo, **params)
            if (error_code > 0):
                break
        except Exception as e:
            error_code = ModuleErrorCode.UPLOAD_FILE_PROCESS if error_code == 0 else ModuleErrorCode.UPLOAD_FILE_EXCEPTION + error_code
            msg_exception= __get_msg_exception(str(e), msg_exception, error_code)
            break

    proc_name = 'UserDataFiles'
    if is_str_none_or_empty(cargo.user_data_file_key):
        pass # pk not ready

    elif (error_code == 0):
        msg_success = cargo.final.get('msg_success', None)
        try:
            UserDataFiles.update(cargo.user_data_file_key, error_code= error_code, success_text= msg_success)
        except Exception as e:
            log_msg= str(e)
            print(log_msg)

    elif (error_code > 0):
        try:
            UserDataFiles.update(cargo.user_data_file_key, error_code= error_code, error_msg= msg_error, error_text= msg_exception)
        except Exception as e:
            error_code = ModuleErrorCode.UPLOAD_FILE_PROCESS + 1
            msg_exception= __get_msg_exception(str(e), msg_exception, error_code)
            print(msg_exception)

    return error_code, msg_error, msg_exception, cargo.final

#eof
"""
    Performs the complete validation process:
        1. Check: file name, validates name, create folders
        2. Register: save process info( user, file, & times) in DB.users_files
        3. Unzip unzip the uploaded file
        4. Submit, sends the file to the `data_validate`
        5. Email, data_validate output is sent via email

        Cargo
            is a class to shares: ProcessData, Params, args, and return values between the 5 modules.

        ProcessData
            is a class that keep the files & folders names

        Params
            is as class that has the values of Configurable parameters of each module


    Part of Canoa `File Validation` Processes

    Equipe da Canoa -- 2024
    mgd
"""

# cSpell:ignore ext

from datetime import datetime

from ...helpers.py_helper import is_str_none_or_empty
from ...config_validate_process import ValidateProcessConfig
from ...helpers.user_helper import LoggedUser, now
from ...helpers.error_helper import ModuleErrorCode
from ..models import UserDataFiles


from .Cargo import Cargo
from .ProcessData import ProcessData

from .check import check
from .unzip import unzip
from .email import email
from .submit import submit
from .register import register


def process(
    logged_user: LoggedUser,
    file_data: object | str,
    proc_data: ProcessData,
    received_at: datetime,
    valid_ext: list[str],
) -> list[int, str, str]:

    from ...shared import app_config, app_log
    current_module_name = __name__.split(".")[-1]

    def _get_next_params(cargo: Cargo) -> list[object, dict]:
        """
        Extracts the parameters of the next procedure,
        initialize cargo and returns to the loop
        """
        params = dict(cargo.next)
        return cargo.init(), params

    def _get_msg_exception(e_str: str, msg_exc: str, code: int) -> str:
        """prepares a complete exception message for the db & log"""
        return f"Upload Error: process.Exception: [{e_str}]; {current_module_name}.Exception: [{msg_exc}], Code [{code}]."

    # Create Cargo, with the parameters for the first procedure (check) of the Loop Process
    cargo = Cargo(
        "2024.09.25_d",
        app_config.DEBUG,
        logged_user,
        ValidateProcessConfig(app_config.DEBUG),
        proc_data,
        received_at,
        {"file_data": file_data, "valid_ext": valid_ext},  # first module parameters
    )
    error_code = 0
    msg_error = ""
    msg_exception = ""

    """
        Process Loop
        runs all the necessary steps (modules) to generate the final `report` and send it by email.

        `proc` Template:
        def proc(cargo: Cargo, param1, param2, ...) -> cargo:
          ''' process ....
    """
    for current_module in [check, register, unzip, submit, email]:
        current_module_name = current_module.__name__
        try:
            cargo, next_module_params = _get_next_params(cargo)
            error_code, msg_error, msg_exception, cargo = current_module(
                cargo, **next_module_params
            )
            if error_code > 0:
                break
        except Exception as e:
            error_code = (
                ModuleErrorCode.RECEIVE_FILE_PROCESS + cargo.step
                if error_code == 0
                else ModuleErrorCode.RECEIVE_FILE_EXCEPTION + error_code
            )
            msg_exception = _get_msg_exception(str(e), msg_exception, error_code)
            msg_error = cargo.default_error if is_str_none_or_empty(msg_error) else msg_error
            break

    current_module_name = "UserDataFiles.update"
    msg_success = cargo.final.get("msg_success", None)
    log_msg = "Processing received file: [{0}] raised error code {1}."
    process_ended = now()

    if is_str_none_or_empty(cargo.table_udf_key):
        pass  # user_data_file's pk not ready
    elif error_code == 0:
        try:
            UserDataFiles.update(
                cargo.table_udf_key,
                error_code=0,
                success_text=msg_success,
                z_process_end_at= process_ended
            )
        except Exception as e:
            app_log.fatal(log_msg, e, 0)
    else:
        try:
            UserDataFiles.update(
                cargo.table_udf_key,
                error_code=error_code,
                success_text=msg_success,  # not really success but standard_output
                # without error, this fields are saved in email.py
                report_ready_at=cargo.report_ready_at,
                e_unzip_started_at=cargo.unzip_started_at,
                f_submit_started_at=cargo.submit_started_at,
                g_email_started_at=cargo.email_started_at,
                z_process_end_at= process_ended,
                error_msg=(
                    "<sem mensagem de erro>"
                    if is_str_none_or_empty(msg_error)
                    else msg_error
                ),
                error_text=msg_exception,
            )

        except Exception as e:
            error_code = ModuleErrorCode.RECEIVE_FILE_PROCESS + 1
            msg_exception = _get_msg_exception(str(e), msg_exception, error_code)
            app_log.fatal(log_msg, msg_exception, error_code, exc_info=error_code)

    return error_code, msg_error, msg_exception, cargo.final


# eof

"""
    Fourth step:
    - Submit to validation

    Part of Canoa `File Validation` Processes

    Equipe da Canoa -- 2024
    mgd
"""
# cSpell:ignore nobuild

import asyncio
import shutil
from os import path, stat

from .Cargo import Cargo
from ...config_upload import DataValidateApp
from ...helpers.py_helper import (
    change_file_ext,
    decode_std_text,
    is_str_none_or_empty,
    now,
)
from ...helpers.error_helper import ModuleErrorCode
from ...shared import app_log


async def _run_validator(
    batch_full_name: str,
    d_v: DataValidateApp,
    input_folder: str,
    output_folder: str,
    debug_validator: bool = False,
):
    #  This function knows quite a lot of how to run [data_validate]

    run_command =  [
                batch_full_name,
                d_v.na_in_folder,  # Named Argument
                input_folder,
                d_v.na_out_folder,
                output_folder,
            ]

    if not is_str_none_or_empty(d_v.flags):
        run_command.append(d_v.flags)

    if debug_validator and not is_str_none_or_empty(d_v.flag_debug):
        run_command.append(d_v.flag_debug)
        app_log.info(' '.join(run_command))
    else:
        app_log.debug(' '.join(run_command))

    # Run the script command asynchronously
    stdout = None
    stderr = None

    try:
        process = await asyncio.create_subprocess_exec(
            *run_command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        # Wait for the process to complete
        stdout, stderr = await process.communicate()

    except Exception as e:
        err_msg = f"{d_v.name}.running: {e}";
        app_log.critical(err_msg)
        return '', err_msg

    # Decode the output from bytes to string
    stdout_str = decode_std_text(stdout)
    stderr_str = decode_std_text(stderr)
    return stdout_str, stderr_str


def submit(cargo: Cargo) -> Cargo:
    """
    Submit the unzip files to app `data_validate` and
    wait for the report

    This function knows all about this app [carranca]
        and nothing about data_validate app
        except the parameters needed to call 'main.py'
    """

    user_report_full_name = "<not produced>"
    msg_error = "uploadFileProcessError"
    error_code = 0
    msg_exception = ""
    task_code = 0
    std_out_str = None
    std_err_str = None

    try:
        task_code += 1  # 1
        # shortcuts
        _cfg = cargo.upload_cfg
        _path = cargo.storage.path
        _path_read = cargo.storage.path.data_tunnel_user_read
        _path_write = cargo.storage.path.data_tunnel_user_write
        batch_full_name = _path.batch_full_name
        if not path.isfile(batch_full_name):  # TODO send to check module
            task_code += 1  # 2
            raise Exception(
                f"The `{_cfg.d_v.name}` module caller [{batch_full_name}] was not found."
            )

        result_ext = _cfg.output_file.ext
        final_report_file_name = f"{_cfg.output_file.name}{result_ext}"
        final_report_full_name = path.join(_path_read, final_report_file_name)

        try:
            task_code += 2  # 3
            std_out_str, std_err_str = asyncio.run(
                _run_validator(
                    batch_full_name,
                    _cfg.d_v,
                    _path_write,
                    _path_read,
                    cargo.in_debug_mode,
                )
            )
            task_code += 1  # 4
        except Exception as e:
            msg_exception = str(e)
            raise Exception(e)

        # Ok, final report should be waiting for us ;—)

        cargo.report_ready_at = now()

        task_code += 1  # 5
        if not path.exists(final_report_full_name):
            task_code += 1  # 6
            raise Exception(f"Report not ready! {_cfg.d_v.name}.stderr: {std_err_str}, {_cfg.d_v.name}.stdout: {std_out_str}")
        elif stat(final_report_full_name).st_size < 200:
            task_code += 2  # 7
            error_code = task_code
        else:
            # copy the final_report file to the same folder and
            # with the same name as the uploaded file:
            user_report_full_name = change_file_ext(
                cargo.storage.user_file_full_name(), result_ext
            )
            task_code += 3  # 8
            shutil.move(final_report_full_name, user_report_full_name)
            task_code += 1  # 9
            error_code = 0 if path.exists(user_report_full_name) else task_code
    except Exception as e:
        error_code = task_code
        msg_exception = str(e)
        app_log.error(msg_exception, exc_info=error_code)
    finally:
        if True:
            try:
                shutil.rmtree(_path_read)
                shutil.rmtree(_path_write)
            except:
                app_log.error('As pastas de comunicação não foram apagadas.')

    # goto email.py
    error_code = (
        0 if (error_code == 0) else error_code + ModuleErrorCode.UPLOAD_FILE_SUBMIT
    )
    return cargo.update(
        error_code,
        msg_error,
        msg_exception,
        {'user_report_full_name': user_report_full_name},
        {'msg_success': std_out_str},
    )

# eof
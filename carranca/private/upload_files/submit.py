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


async def _run_validator(
    batch_full_name: str,
    app: DataValidateApp,
    input_folder: str,
    output_folder: str,
    debug_validator: bool = False,
):
    #  This function knows quite a lot of how to run [data_validate]

    run_command = [
        batch_full_name,
        app.na_in_folder,  # Named Argument
        input_folder,
        app.na_out_folder,
        output_folder,
        app.flags,
    ]

    if debug_validator and not is_str_none_or_empty(app.flag_debug):
        run_command.append(app.flag_debug)
        print(' '.join(run_command))  # TODO  LOG

    print(' '.join(run_command))  # TODO  LOG

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
        return '', f"{app.name}.running: {e}"

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
    stdout_str = None
    external_error = False
    report_ready = False

    try:
        task_code += 1  # 1
        # shortcuts
        _cfg = cargo.upload_cfg
        _path = cargo.storage.path
        _path_read = cargo.storage.path.data_tunnel_user_read
        _path_write = cargo.storage.path.data_tunnel_user_write
        external_app_path = path.join(_path.apps_parent_path, _cfg.app.name)
        batch_full_name = path.join(external_app_path, _cfg.app.batch)
        print(batch_full_name)
        if not path.exists(batch_full_name):  # TODO send to check module
            task_code += 1  # 2
            raise Exception(
                f"The `{_cfg.app.name}` module caller [{batch_full_name}] was not found."
            )

        result_ext = _cfg.output_file.ext
        final_report_file_name = f"{_cfg.output_file.name}{result_ext}"
        final_report_full_name = path.join(_path_read, final_report_file_name)

        try:
            task_code += 2  # 3
            stdout_str, stderr_str = asyncio.run(
                _run_validator(
                    batch_full_name,
                    _cfg.app,
                    _path_write,
                    _path_read,
                    cargo.in_debug_mode,
                )
            )
            task_code += 1  # 4
            external_error = not is_str_none_or_empty(stderr_str)
            report_ready = path.exists(final_report_full_name)
            if external_error and not report_ready:
                raise Exception(f"{_cfg.app.name}.stderr: {stderr_str}")
        except Exception as e:
            external_error = True
            msg_exception = str(e)
            raise Exception(e)

        # Ok, final report should be waiting for us ;—)

        cargo.report_ready_at = now()

        task_code += 1  # 5
        if not report_ready:
            task_code += 1  # 6
            error_code = task_code
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
        print(msg_exception)  # TODO  log
    finally:
        try:
            shutil.rmtree(_path_read)
            shutil.rmtree(_path_write)
        except:
            print('As pastas de comunicação não foram apagadas.')  # TODO  log

    # goto email.py
    error_code = (
        0 if (error_code == 0) else error_code + ModuleErrorCode.UPLOAD_FILE_SUBMIT
    )
    return cargo.update(
        error_code,
        msg_error,
        msg_exception,
        {'user_report_full_name': user_report_full_name},
        {'msg_success': stdout_str},
    )

# eof
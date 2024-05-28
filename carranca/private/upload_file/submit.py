# Equipe da Canoa -- 2024
#
# mgd
# cSpell:ignore nobuild
"""
Fourth step:
  - Submit to validation

Part of Canoa `File Validation` Processes
"""
import asyncio
import shutil
from os import path, stat

from .Cargo import Cargo
from ...helpers.py_helper import change_file_ext, is_str_none_or_empty, now
from ...helpers.error_helper import ModuleErrorCode

async def _run_validator(apps_parent_path: str, cfg: object, input_folder: str, output_folder: str, debug_validator: bool = False):
    #  This function knows quite a lot of how to run [data_validate]

    external_app_path = path.join(apps_parent_path, cfg.app_name)
    batch_full_name = path.join(external_app_path, cfg.batch_file_name)
    run_command = [batch_full_name, "--input_folder", input_folder, "--output_folder", output_folder, cfg.args]

    if debug_validator:
        run_command.add("--debug")

    # Run the script command asynchronously
    stdout = None
    stderr = None
    script= " ".join(run_command)
    try:
        process = await asyncio.create_subprocess_exec(
            *run_command, stdout = asyncio.subprocess.PIPE, stderr = asyncio.subprocess.PIPE
        )

        # Wait for the process to complete
        stdout, stderr = await process.communicate()

    except Exception as e:
        return '', f"{cfg.app_name}.running: {e}"

    # Decode the output from bytes to string
    stdout_str = ""
    stderr_str = ""
    try:
        stdout_str = "" if stdout == None else stdout.decode()
        stderr_str = "" if stderr == None else stderr.decode()
    except Exception as e:
        return '', f"{cfg.app_name}.reading_output: {e}"

    return stdout_str, stderr_str


def submit(cargo: Cargo) -> Cargo:
    """
    Submit the unzip files to app `data_validate` and
    wait for the report

    This function knows all about this app [carranca]
        and nothing about data_validate app
        except the parameters needed to call 'main.py'
    """

    user_report_full_name = '<not produced>'
    msg_error = 'uploadFileProcessError'
    error_code = 0
    msg_exception = ''
    task_code = 0

    stdout_str = None

    try:
        data_validate_cfg= cargo.storage.data_validate

        try:
            _path = cargo.storage.path
            task_code= 1 #1
            stdout_str, stderr_str = asyncio.run(_run_validator(_path.apps_parent_path, data_validate_cfg, _path.data_tunnel_user_write, _path.data_tunnel_user_read, False))
            task_code+= 1 #2
            if not is_str_none_or_empty(stderr_str):
                raise Exception(f"{data_validate_cfg.app_name}.stderr: {stderr_str}")
        except Exception as e:
            msg_exception = str(e)
            raise Exception(e)


        # Ok, final report should be waiting for us ;—)

        cargo.report_ready_at = now()

        task_code+= 1  #3
        result_ext = data_validate_cfg.file_ext
        final_report_file_name = f"{data_validate_cfg.file_name}{result_ext}"
        final_report_full_name = path.join(cargo.storage.path.data_tunnel_user_read, final_report_file_name)
        if not path.exists(final_report_full_name):
            task_code+= 1  #4
            error_code= task_code
        elif stat(final_report_full_name).st_size < 200:
            task_code+= 2  #5
            error_code= task_code
        else:
            # copy the final_report file to the same folder and
            # with the same name as the uploaded file:
            user_report_full_name = change_file_ext(cargo.storage.user_file_full_name(), result_ext)
            task_code+= 3  #6
            shutil.move(final_report_full_name, user_report_full_name)
            task_code+= 4  #7
            error_code = 0 if path.exists(user_report_full_name) else task_code
            try:
                task_code+= 1  #8
                shutil.rmtree(cargo.storage.path.data_tunnel_user_read)
                shutil.rmtree(cargo.storage.path.data_tunnel_user_write)
            except:
                print('As pastas de comunicação não foram apagadas.')  #TODO  log

    except Exception as e:
        error_code = task_code
        msg_exception = str(e)
        print(msg_exception)  #TODO  log

    # goto email.py
    error_code = 0 if (error_code == 0) else error_code + ModuleErrorCode.UPLOAD_FILE_SUBMIT
    return cargo.update(error_code, msg_error, msg_exception, {'user_report_full_name': user_report_full_name}, {'msg_success':  stdout_str })

#eof

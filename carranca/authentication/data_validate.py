"""
 Equipe da Canoa -- 2024

 mgd 2024-04-07
"""

# cSpell:ignore werkzeug

import asyncio
import shutil
from os import makedirs, path, stat
import zipfile


from ..scripts.pyHelper import change_file_ext, path_remove_last
from ..scripts.carranca_config import CarrancaConfig


# -------------------------------------------------------------------
#  This function knows all about module [data_validate]
async def _run_validator(file_common: str, file_folder: str, debug_validator: bool = False):
    module = "data_validate"
    script = "main.py"
    script_name = path.join(file_common, module, script)
    script_command = [
        "python",
        script_name,
        "--input_folder",
        file_folder,
        "--output_folder",
        file_folder,
        "--no-spellchecker"
    ]

    if debug_validator:
        script_command.add("--debug")

    # Run the script command asynchronously
    stdout = None
    stderr = None
    script= " ".join(script_command)
    try:
        process = await asyncio.create_subprocess_exec(
            *script_command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        # Wait for the process to complete
        stdout, stderr = await process.communicate()

    except Exception as e:
        print(f"Error running {script}: {e}")
        return '', 'Internal Error'


    # Decode the output from bytes to string
    stdout_str = ""
    stderr_str = ""
    try:
        stdout_str = "" if stdout == None else stdout.decode()
        stderr_str = "" if stderr == None else stderr.decode()
    except Exception as e:
        print('Output error in data_validate' + e)
        stdout_str = ""
        stderr_str = ""

    return stdout_str, stderr_str
# -------------------------------------------------------------------

# ====================================================================
# This function knows all about module [carranca]
def submit_to_data_validate(source_folder: str, file_name: str, user_code: str):
    """
     Calls data_validate module and returns:
     error_code: 0 if ok else [1 .. 26]
     msg_str:    a msg_str (db.ui_items)
     result:     the htm/pfd file name with the results

    """
    msg_err = "uploadFileError"
    error_code = 0
    task_code = 1

    # Run the validator, proc_code: [10|20, 16|26]
    result = ""
    task_code= 10
    try:
        msg_err = "uploadFileProcessError"
        try:
            asyncio.run(_run_validator(folder_common, destiny_folder))
        except:
            task_code+= 10  # An error could have occurred after `report` was created

        # check if the file exists
        task_code+= 1  # 11|21
        result_ext = ".html"
        report = path.join(destiny_folder, f"report{result_ext}")
        task_code+= 1  # 12|22
        if not path.exists(report):
            task_code+= 1  # 13|23
            error_code= task_code
        elif stat(report).st_size < 40:
            task_code+= 2  # 14|24
            error_code= task_code
        else:
            msg_err = "uploadFileError"
            file = change_file_ext(file_name, result_ext)
            result = path.join(source_folder, file)
            task_code+= 3  # 15|25
            shutil.copy(report, result)
            task_code+= 1  # 16|26
            error_code = 0 if path.exists(result) else task_code

    except Exception as e:
        error_code = task_code
        print(e)  #TODO save error


    #shutil.rmtree(destiny_folder)
    msg_err = "uploadFileSuccess" if error_code == 0 else msg_err
    return error_code, msg_err, result

#eof
"""
 Equipe da Canoa -- 2024

 mgd 2024-04-07
"""

# cSpell:ignore werkzeug

import asyncio
import shutil
from os import  path, stat

from ..scripts.pyHelper import change_file_ext


# -------------------------------------------------------------------
#  This function knows all about module [data_validate]
async def _run_validator(file_common: str, input_folder: str, output_folder: str, debug_validator: bool = False):
    module = "data_validate"
    script = "main.py"
    script_name = path.join(file_common, module, script)
    script_command = [
        "python",
        script_name,
        "--input_folder",
        input_folder,
        "--output_folder",
        output_folder,
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
def submit_to_data_validate(task_code: int, uploaded_file_name: str, folder_common: str, validate_input_path: str, validate_output_path: str):
    """
     This function knows all about this module [carranca]
        and nothing about data_validate
        except the parameters needed to call 'main.py'
     Calls data_validate module and returns:
     error_code: 0 if ok else task_code+[0 .. 36]
     msg_err:    a msg_str (db.ui_items)
     result:     the htm/pfd file name with the results

    """
    # Run the validator, proc_code: task_code+=[0|10, 6|16]

    except_msg = ''
    msg_err = ''
    error_code = 0
    file_name_result = ""
    msg_err = "uploadFileProcessError"

    try:
        try:
            asyncio.run(_run_validator(folder_common, validate_input_path, validate_output_path, False))
        except:
            task_code+= 10  # An error occurred but maybe the `report` was created

        # check if the file exists
        task_code+= 1  #tc+[1|11]
        result_ext = ".html"
        report = path.join(validate_output_path, f"report{result_ext}")
        task_code+= 1  #tc+[2|12]
        if not path.exists(report):
            task_code+= 1  #tc+[3|13]
            error_code= task_code
        elif stat(report).st_size < 200:
            task_code+= 2  #tc+[4|14]
            error_code= task_code
        else:
            msg_err = "uploadFileError"
            file = change_file_ext(uploaded_file_name, result_ext)
            file_name_result = path.join(validate_input_path, file)
            task_code+= 3  #tc+[5|15]
            shutil.copy(report, file_name_result)
            task_code+= 1  #tc+[6|16]
            error_code = 0 if path.exists(file_name_result) else task_code

    except Exception as e:
        error_code = task_code
        except_msg = str(e)
        print(except_msg)  #TODO  log

    return error_code, msg_err, except_msg, file_name_result

#eof
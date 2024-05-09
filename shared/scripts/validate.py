import asyncio
import re
import shutil
from os import makedirs, path
import zipfile

from .pyHelper import change_file_ext, path_remove_last
from .carranca_shared_info import CarrancaSharedInfo


# ====================================================================
def _find_err_and_warn(text):
    # Define the regex pattern to find X and Y
    pattern = r"Número de erros: (\d+)\s+Número de avisos: (\d+)"

    # Search for the pattern in the text
    match = re.search(pattern, text)

    # If the pattern is found, extract X and Y
    if match:
        err = int(match.group(1))
        wrn = int(match.group(2))
        return err, wrn
    else:
        return None, None


# ====================================================================
#  This function knows all about module [data_validate]
async def _run_validator(file_common, file_folder: str):
    module = "data_validate"
    script = "main.py"
    script_name = path.join(file_common, module, script)
    script_command = [
        "python3",
        script_name,
        "--input_folder",
        file_folder,
        "--no-spellchecker",
        "--lang-dict=pt",
        "--debug",
    ]


    # Run the script command asynchronously
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
    stdout_str = stdout.decode()
    stderr_str = stderr.decode()
    stderr_str = '' if stderr.strip() == b'' else 'Some error'
    stdout_str = ''

    return stdout_str, stderr_str
# -------------------------------------------------------------------

# ====================================================================
#  This function knows all about module [carranca]
def send_to_validate(source_folder: str, file_name: str, user_code: str):
    msg_str = ''
    error_code = 0
    code = 1
    source = path.join(source_folder, file_name)

    # Unzip file in data_tunnel folder
    try:
        folder_common = path_remove_last(CarrancaSharedInfo.folder_data_tunnel)
        code+= 1
        destiny_folder = path.join(CarrancaSharedInfo.folder_data_tunnel, user_code)
        if not path.isdir(destiny_folder):
            code+= 1
            makedirs(destiny_folder)

        # check & unzip
        code+= 1
        msg_str= "uploadFileZip_unknown"
        with zipfile.ZipFile(source, 'r') as zip_file:
            if zip_file.testzip() is not None:
                code+= 1
                msg_str= "uploadFileZip_corrupted"
            else:
                code+= 2
                msg_str = "uploadFileZip_extraction_error"
                zip_file.extractall(destiny_folder)

    except:
        error_code = code
        return error_code, msg_str, "", ""


    # Run the validator
    result = ""
    info_str = ''
    try:
        code= 10
        stdout, stderr = asyncio.run(_run_validator(folder_common, destiny_folder))
        code+= 1
        report = path.join(destiny_folder, 'report.pdf')
        file_pdf = change_file_ext(file_name, '.pdf')
        result = path.join(source_folder, file_pdf)
        if path.exists(report):
            code+= 1
            shutil.copy(report, result)
            code = 0 if path.exists(result) else code
        else:
            code+= 1

        error_code = code
    except:
        error_code = code

    shutil.rmtree(destiny_folder)
    msg_str = "uploadFileSuccess" if error_code == 0 else "uploadFileProcessError"
    return error_code, msg_str, info_str, result

    # if is_str_none_or_empty(stderr) and is_str_none_or_empty(stdout): # nothing returned by the validator
    #     error_code = code + 1
    #     msg_str = "uploadFileError"

    # elif is_str_none_or_empty(stderr): # No error
    #     error_code = 0
    #     msg, wrn = _find_err_and_warn(stdout)
    #     info_str = f"Quantidade de erros: {msg}, de avisos {wrn}."
    #     msg_str= "uploadFileSuccess"

    # else:
    #     error_code = 0
    #     msg_str = "uploadFileWarning"

    # return error_code, msg_str, info_str

    # send e-mail
# -------------------------------------------------------------------

#eof
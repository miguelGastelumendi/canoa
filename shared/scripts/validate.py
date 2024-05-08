import asyncio
import re
from os import makedirs, path
import zipfile
from shared.scripts.pyHelper import is_str_none_or_empty, path_remove_last
from .carranca_shared_info import CarrancaSharedInfo
from .ansiToHTML import ansi_to_html

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
    except Exception as e:
        print(f"Error running {script}: {e}")
        return '', 'Internal Error'

    # Wait for the process to complete
    stdout, stderr = await process.communicate()

    # Decode the output from bytes to string
    stdout_str = ansi_to_html(stdout.decode())
    stderr_str = ansi_to_html(stderr.decode())

    return stdout_str, stderr_str
# -------------------------------------------------------------------

# ====================================================================
#  This function knows all about module [carranca]
def send_to_validate(file_folder: str, file_name: str, user_code: str):

    msg_str = ''
    error_code = 0
    code = 1
    source = path.join(file_folder, file_name)

    try:
        folder_common = path_remove_last(CarrancaSharedInfo.folder_channel)
        code+= 1
        destiny_folder = path.join(CarrancaSharedInfo.folder_channel, user_code)
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

    except Exception as e:
        error_code = code

    if (error_code > 0):
        return error_code, msg_str

    stdout, stderr = asyncio.run(_run_validator(folder_common, destiny_folder))

    msg_str = ''
    # print("Standard Output:", stdout)
    # print("Standard Error:", stderr)
    code= +1
    if is_str_none_or_empty(stderr) and is_str_none_or_empty(stdout):
        error_code = code + 1

    elif is_str_none_or_empty(stderr):
        error_code = 0
        msg, wrn = _find_err_and_warn(stdout)
        msg_str= f"Quantidade de erros: {msg}, de avisos {wrn}."

    else:
        error_code = code + 2
        msg_str = "Aguarde o resultado."

    return error_code, msg_str

    # send e-mail
# -------------------------------------------------------------------

#eof
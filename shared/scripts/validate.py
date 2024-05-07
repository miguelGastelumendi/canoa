import asyncio
import shutil
from os import makedirs, path
from shared.scripts.pyHelper import path_remove_last
from .carranca_shared_info import CarrancaSharedInfo

# ====================================================================
#  This function knows all about module [data_validate]
async def _run_validator(file_common, file_folder: str, file_name: str):
    module = "data_validate"
    script = "main.py"
    script_name = path.join(file_common, module , script)
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
    process = await asyncio.create_subprocess_exec(
        *script_command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    # Wait for the process to complete
    stdout, stderr = await process.communicate()

    # Decode the output from bytes to string
    stdout_str = stdout.decode()
    stderr_str = stderr.decode()

    return stdout_str, stderr_str
# -------------------------------------------------------------------

# ====================================================================
#  This function knows all about module [carranca]
async def data_validate(file_folder: str, file_name: str, user_code: str):
    source = path.join(file_folder, file_name)

    #TODO if (working) raise Error
    folder_common = path_remove_last(CarrancaSharedInfo.folder_channel)
    destiny_folder = path.join(CarrancaSharedInfo.folder_channel, user_code)
    if not path.isdir(destiny_folder):
        makedirs(destiny_folder)

    destiny = path.join(destiny_folder, file_name)
    shutil.copy2(source, destiny)

    stdout, stderr = await _run_validator(folder_common, destiny_folder, file_name)

    print("Standard Output:", stdout)
    print("Standard Error:", stderr)
    # convert
    # send e-mail
# -------------------------------------------------------------------

#eof
"""
 Equipe da Canoa -- 2024

 mgd 2024-04-07
"""

# cSpell:ignore
from os import path, makedirs
from zlib import crc32
from carranca import db

from .models import UserDataFiles
from ..scripts.email_sender import send_email
from ..scripts.pyHelper import current_milliseconds, is_str_none_or_empty, now
from ..scripts.textsHelper import get_section, add_msg_success, add_msg_error
from ..scripts.carranca_config import CarrancaConfig

from data_validate import submit_to_data_validate

# { do_uploaded_files_folder ==============================
def do_uploaded_files_folder(uploaded_files_folder) -> bool:
    done = os.path.isdir(uploaded_files_folder)
    try:
        if not done:
            os.makedirs(uploaded_files_folder)
            done = True
    except Exception as e:
        done = False
        #logger(f"Error {task_code} while {task}, {e}")

    return done
# do_uploaded_files_folder } ------------------------------


# { _save_file_and_record =================================
def _save_file_and_record(user_id: int, file_obj, file_folder: str, file_ticket: str, file_name_secure: str):
    """
        Persist upload file into UserDataFiles table
        task_code = [0, 8]
    """
    error_code = 0
    file_saved = False
    file_name = ''
    file_full_name =''
    task_code = 0
    try:
        # make unique file name
        file_name = f"{file_ticket}_{file_name_secure}"

        file_size = 0
        file_crc32 = 0
        file_full_name = os.path.join(file_folder, file_name)

        with open(file_full_name, "wb") as file:
            task_code+= 1 #1
            file_data = file_obj.read()
            task_code+= 1 #2
            file_crc32 = crc32(file_data)
            task_code+= 1 #3
            file_size = file.write(file_data)
            file_saved = True

        #save a record for this operation
        task = 'registering file'
        task_code= 6 #6
        df = UserDataFiles(
            id_users = user_id
            , file_size = file_size
            , file_crc32 = file_crc32
            , file_name = file_name_secure
            , ticket = file_ticket
        )
        task_code+= 1 #7
        db.session.add(df)
        task_code+= 1 #8
        db.session.commit()
    except Exception as e:
        error_code = task_code
        #logger(f"Error {task_code} while {task}, {e}")

    return error_code, file_saved, file_name, file_full_name

# _save_file_and_record } ---------------------------------
# { _unzip_file ===========================================

def _unzip_file(source_folder: str, file_name: str, user_code: str):
    """
     Unzips the file
     error_code: 0 if ok else [1 .. 26]
     msg_str:    a msg_str (db.ui_items)
     result:     the htm/pfd file name with the results

    """

    msg_err = "uploadFileError"
    task_code = 0

    # Unzip file in data_tunnel folder, proc_code: [1, 8]
    try:
        task_code+= 1  #01

        task_code+= 1  #02
        destiny_folder = path.join(CarrancaConfig.folder_data_tunnel, user_code)
        task_code+= 1  #03
        if path.isdir(destiny_folder):
            task_code+= 1 #04
        else:
            task_code+= 1 #04
            makedirs(destiny_folder)

        # check & unzip
        task_code+= 1 #05
        source = path.join(source_folder, file_name)
        msg_err= "uploadFileZip_unknown"
        task_code+= 1 #06
        with zipfile.ZipFile(source, 'r') as zip_file:
            if zip_file.testzip() is not None:
                task_code+= 1 #07
                msg_err= "uploadFileZip_corrupted"
                error_code = task_code
            else:
                task_code+= 2 #08
                msg_err = "uploadFileZip_extraction_error"
                zip_file.extractall(destiny_folder)

    except:
        error_code= task_code

    if (error_code != 0):
        return error_code, msg_err, ""

# _unzip_file } -------------------------------------------

# { data_validate =========================================
def data_validate(current_user: any, user_code: str, file_obj, uploaded_files_folder: str, file_name_secure: str):
    """
        saves the file, records in table user_data_files, submits to data validation and sends an email
        task_code ->
            save & record: [1..8]
            submit: [10, 11|21.. 15|25]
            email: [30]
    """
    file_saved = False
    file_full_name = ''
    error_msg = 'uploadFileError' # one of ui_text.name, id_section=2 (error)
    task_code = 0

    # ticket or 'número de protocolo'
    file_ticket = f"{user_code}_{now().strftime('%Y-%m-%d')}_{current_milliseconds():08d}"

    # save the file to storage & register in table task [0..8]
    task_code, file_saved, file_name, file_full_name = _save_file_and_record(current_user.id, file_obj, uploaded_files_folder, file_ticket, file_name_secure)
    if (task_code > 0):
        return task_code, error_msg


    try:

        # send to validate (project `data_validate`) [10..25]
        task_code, error_msg, file_result = submit_to_data_validate(uploaded_files_folder, file_name, user_code)

        if task_code > 0:
            return task_code, error_msg
AQUI
        task_code = 30
        send_email(current_user.email, "emailUploadedFile", {'url': ''}, file_result)

    except Exception as e:
        try:
            except_error = str(e)
            UserDataFiles.update(file_ticket, error_code= err_code, error_msg= except_error)
            if file_saved:
                os.remove(file_full_name)
                removed = " File removed | "

        except Exception as x:
            print("Error removing file or updating `UserDataFile` {x}")
            #logger(f"Error removing file or updating `UserDataFile` {x}", 'err')


    return task_code, error_msg
# data_validate } -----------------------------------------
#eof

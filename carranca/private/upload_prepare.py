# Equipe da Canoa -- 2024
#
# mgd 2024-05-09,15
# cSpell:ignore


import zipfile
import os
from zlib import crc32
from carranca import db

from .models import UserDataFiles
from .data_validate import submit_to_data_validate
from ..helpers.py_helper import current_milliseconds, path_remove_last, to_base, now
from ..helpers.user_helper import now_as_text
from ..helpers.email_helper import send_email


def _save_file_and_record(task_code: int, user_id: int, file_obj, file_folder: str, file_ticket: str, file_name_secure: str):
    """
        Persist upload file into UserDataFiles table
        task_code = tc+[0, 8]
    """
    error_code = 0
    file_saved = False
    file_registered = False
    file_name = ''
    file_full_name =''
    try:
        # make unique file name
        file_name = f"{file_ticket}_{file_name_secure}"

        file_size = 0
        file_crc32 = 0
        file_full_name = os.path.join(file_folder, file_name)
        task = 'reading file'
        with open(file_full_name, "wb") as file:
            task_code+= 1 #tc+1
            file_data = file_obj.read()
            task_code+= 1 #tc+2
            file_crc32 = crc32(file_data)
            task_code+= 1 #tc+3
            file_size = file.write(file_data)
            file_saved = True

        #save a record for this operation
        task = 'registering file'
        task_code+= 3 #tc+6
        record = UserDataFiles(
            id_users = user_id
            , file_size = file_size
            , file_crc32 = file_crc32
            , file_name = file_name_secure
            , ticket = file_ticket
        )
        task_code+= 1 #tc+7
        db.session.add(record)
        task_code+= 1 #tc+8
        db.session.commit()
        file_registered = True
    except Exception as e:
        error_code = task_code
        if file_saved and not file_registered:
            os.remove(file_full_name)
        #logger(f"Error {task_code} while {task}, {e}")

    return error_code, file_full_name


def _unzip_file(task_code: int, upload_zip_file: str, unzip_folder: str):
    """
     Unzips the file
     error_code: 0 if ok else [1 .. 5]
     msg_err:    a msg_err (db.ui_items)
    """

    msg_err = "uploadFileError"
    error_code = 0

    # Unzip file in data_tunnel folder, task_code: [1, 6]
    task_code+= 1  #tc+1
    if not folder_must_exist(unzip_folder):
        return task_code, msg_err

    try:
        # check & unzip
        task_code+= 1 #tc+2
        msg_err= "uploadFileZip_unknown"
        task_code+= 1 #tc+4
        with zipfile.ZipFile(upload_zip_file, 'r') as zip_file:
            if zip_file.testzip() is not None:
                task_code+= 1 #tc+4
                msg_err= "uploadFileZip_corrupted"
                raise RuntimeError(msg_err)
            else:
                task_code+= 2 #tc+5
                msg_err = "uploadFileZip_extraction_error"
                zip_file.extractall(unzip_folder)

    except:
        error_code= task_code

    return error_code, msg_err


def data_validate(task_code: int, current_user: any, user_code: str, file_obj,  file_name_secure: str, uploaded_files_folder: str, user_data_tunnel_path: str):
    """
        saves the file, records in user_data_file stable, submits to data validation and sends an email
        task_code ->
            save & record: [1..8]
            submit: [10, 11|21.. 15|25] +10 if module didn't finish
            email: [30]
    """

    # one of ui_text.name, id_section=2 (error)
    error_msg = 'uploadFileError'
    except_msg = ''
    error_code = 0

    # ticket or 'número de protocolo'
    ms = to_base(current_milliseconds(), 22).zfill(6)  # max ggi.48g
    file_ticket = f"{user_code}_{now().strftime('%Y-%m-%d')}_{ms}"
    email_params = {'ticket': file_ticket, 'when': now_as_text()}

    # save the user-file to storage & register in table task 1+[0..8]
    task_code+= 0 #tc+= 0
    error_code, uploaded_zip_file = _save_file_and_record(task_code, current_user.id, file_obj, uploaded_files_folder, file_ticket, file_name_secure)
    if (error_code > 0):
        return error_code, error_msg, ''

    try:
        # error_code = 0
        # unzip the user-file on the common folder 10 + [1..6]
        task_code+= 10 #tc+= 10
        common_folder = path_remove_last(CarrancaConfig.path_data_tunnel)
        validate_input_path = user_data_tunnel_path
        validate_output_path = user_data_tunnel_path # BUG os.path.join(validate_input_path, CarrancaConfig.folder_validate_output)

        error_code, error_msg = _unzip_file(task_code, uploaded_zip_file, validate_input_path)

        if error_code == 0:
            # send to validate (project `data_validate`) 20+[0|10, 6|16]
            task_code+= 10 #tc+= 20
        #    error_code, error_msg, except_msg, file_name_result = submit_to_data_validate(task_code, uploaded_zip_file, common_folder, validate_input_path, validate_output_path)

        if error_code == 0:
            task_code+= 20 #tc+= 40
            error_msg = "uploadFileEmailFailed"
            if send_email(current_user.email, "uploadedFile_email", email_params, file_name_result):
                task_code+= 1 #tc+41
                UserDataFiles.update(file_ticket, email_sent= True)
            else:
                task_code+= 2
                raise RuntimeError(error_msg)
    except Exception as e:
        error_code = task_code if error_code == 0 else error_code
        except_msg = str(e)

    if error_code > 0:
        try:
            UserDataFiles.update(file_ticket, error_code= error_code, error_msg= f"{error_msg} Exception: [{except_msg}].")
        except Exception as e:
            print(e)
            #app.app.logger.error(f"Error removing file or updating `UserDataFile` [{x}].")


    return error_code, ('uploadFileSuccess' if error_code == 0 else error_msg), file_ticket


#eof

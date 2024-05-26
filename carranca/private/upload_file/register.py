# Equipe da Canoa -- 2024
#
# mgd
# cSpell:ignore
"""
Second step:
  - Save the file with a unique name in Uploaded_file
  - Create a record in table user_data_files (UserDataFiles)

Part of Canoa `File Validation` Processes
"""
import os
from zlib import crc32
from carranca import db

from ...helpers.py_helper import current_milliseconds, to_base, now
from ...helpers.error_helper import ModuleErrorCode
from ..models import UserDataFiles

from .Cargo import Cargo

def register(cargo: Cargo, file_obj: object) -> Cargo:

    error_code = 0
    msg_exception = ''
    task_code = 0

    file_saved = False
    file_registered = False
    user_file_full_name =''

    ms = to_base(current_milliseconds(), 22).zfill(6)  # max = ggi.48g
    file_ticket = f"{cargo.user.code}_{now().strftime('%Y-%m-%d')}_{ms}"

    try:
        ''' This is a unique column in UserDataFiles, use for updates '''
        cargo.user_data_file_key = file_ticket
        # make unique file name
        cargo.storage.user_file_name = f"{file_ticket}_{cargo.storage.uploaded_file_name}"
        user_file_full_name = cargo.storage.user_file_full_name()

        file_size = 0
        file_crc32 = 0
        # create the uploaded_file, from file_obj
        with open(user_file_full_name, "wb") as file:
            task_code += 1 # +1
            file_data = file_obj.read()
            task_code += 1 # +2
            file_crc32 = crc32(file_data)
            task_code += 1 # +3
            file_size = file.write(file_data)
            file_saved = True

        #save a record for this operation
        task_code += 1 # +4
        record = UserDataFiles(
            id_users = cargo.user.id
            , file_size = file_size
            , file_crc32 = file_crc32
            , file_name = cargo.storage.uploaded_file_name
            , ticket = file_ticket
            , upload_start_at = cargo.started_at
        )
        task_code += 1 # +5
        db.session.add(record)
        task_code += 1 # +6
        db.session.commit()
        file_registered = True
        task_code = 0 # very important
    except Exception as e:
        task_code += 10
        msg_exception= str(e)
        if file_saved and not file_registered:
            os.remove(user_file_full_name)


    # goto unzip
    error_code = 0 if task_code == 0 else ModuleErrorCode.UPLOAD_FILE_REGISTER + task_code
    return cargo.update(error_code, '', msg_exception, {}, {'file_ticket': file_ticket})

#eof

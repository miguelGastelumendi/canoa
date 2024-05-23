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

from upload_file_process import Cargo
from upload_storage import UploadStorage
from ..helpers.py_helper import current_milliseconds, path_remove_last, to_base, now

def upload_file_register(cargo: Cargo, file_obj: object, upload_storage: UploadStorage) -> Cargo:

    task_code = 0
    error_code = 0
    file_saved = False
    file_registered = False
    file_name = ''
    file_full_name =''

    ms = to_base(current_milliseconds(), 22).zfill(6)  # max = ggi.48g
    file_ticket = f"{user_code}_{now().strftime('%Y-%m-%d')}_{ms}"

    try:
        # make unique file name
        file_name = f"{file_ticket}_{file_name}"

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
            , file_name = file_name
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



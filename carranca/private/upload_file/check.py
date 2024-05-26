# Equipe da Canoa -- 2024
#
# mgd
# cSpell:ignore werkzeug ext
"""
First step:
  - Simple file validations
  - Check if exist or create process folders

Part of Canoa `File Validation` Processes
"""
from os import path
from werkzeug.utils import secure_filename

from ...helpers.error_helper import ModuleErrorCode
from ...helpers.py_helper import (folder_must_exist, is_same_file_name, is_str_none_or_empty)

from .Cargo import Cargo


def check(cargo: Cargo, file_obj: object, valid_ext: list[str]) -> Cargo:

    error_code = 0
    msg_exception = ''
    task_code = 0

    try:
        cargo.storage.uploaded_file_name = None if file_obj == None else secure_filename(file_obj.filename)

        if file_obj == None:
            task_code = 1
        elif is_str_none_or_empty(cargo.user.email):
            task_code = 2
        elif is_str_none_or_empty(cargo.storage.uploaded_file_name):
            task_code = 3
        elif is_str_none_or_empty(cargo.storage.data_validate.file_name):
            task_code = 4
        elif is_str_none_or_empty(cargo.storage.data_validate.file_ext):
            task_code = 5
        elif not is_same_file_name(file_obj.filename, cargo.storage.uploaded_file_name):
            # invalid name, be careful
            task_code = 6
        elif len(cargo.storage.uploaded_file_name) > 80:
            # UserDataFiles.file_name.length
            task_code = 6
        elif not any(cargo.storage.uploaded_file_name.lower().endswith(ext.strip().lower()) for ext in valid_ext):
            # lower() is to much Windows?
            task_code = 7
        # elif not response.headers.get('Content-Type') == ct in valid_content_types.split(',')): #check if really zip
            # task_code+= 9
        elif not folder_must_exist(cargo.storage.path.user):
            task_code = 10
        elif not folder_must_exist(cargo.storage.path.data_tunnel_user_read):
            task_code = 11
        elif not folder_must_exist(cargo.storage.path.data_tunnel_user_write):
            task_code = 12
        # elif not path.exists(file_obj.filename): #????
        #     task_code = 13
        else:
            task_code = 0
    except Exception as e:
        msg_exception= str(e)
        task_code = 19 # is the highest possible (see ModuleErrorCode.UPLOAD_FILE_CHECK + 1)


    # goto register.py
    error_code = 0 if task_code == 0 else ModuleErrorCode.UPLOAD_FILE_CHECK + task_code
    return cargo.update(error_code, '', msg_exception, {'file_obj': file_obj})

# eof

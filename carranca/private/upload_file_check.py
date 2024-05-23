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
from main import app_config
from upload_file_process import Cargo

from ..helpers.py_helper import (folder_must_exist, is_same_file_name, is_str_none_or_empty)
from ..helpers.error_helper import ModuleErrorCode
from upload_storage import UploadStorage


def upload_file_check(cargo: Cargo, current_user: object, file_obj: object, valid_ext: list[str]) -> Cargo:

    exception_error = ''
    task_code = 0
    try:
        user_code = user_code(current_user.id)
        file_name_secure = None if file_obj == None else secure_filename(file_obj.filename)
        upload_storage = UploadStorage(user_code, app_config, file_name_secure)

        if file_obj == None:
            task_code += 1
        elif is_str_none_or_empty(current_user.email):
            task_code += 2
        elif is_str_none_or_empty(file_name_secure):
            task_code += 3
        elif not is_same_file_name(file_obj.filename, file_name_secure):
            # invalid name, be careful
            task_code += 4
        elif len(file_name_secure) > 130:
            # UserDataFiles.file_name.length
            task_code += 5
        elif not any(file_name_secure.lower().endswith(ext.strip()) for ext in valid_ext):
            task_code += 6
        # elif not response.headers.get('Content-Type') == ct in valid_content_types.split(',')): #check if really zip
        # task_code+= 7
        elif not folder_must_exist(upload_storage.path.uploaded_files):
            task_code += 8
        elif not folder_must_exist(upload_storage.path.uploaded_files):
            task_code += 9
        elif not folder_must_exist(upload_storage.path.data_tunnel_user_read):
            task_code += 10
        elif not path.exists(file_obj.file_obj.filename):
            task_code += 11
        else:
            task_code = 0
    except Exception as e:
        exception_error= str(e)
        task_code+ 14


    error_code = 0 if task_code == 0 else ModuleErrorCode.UPLOAD_FILE_CHECK + task_code
    next = {'file_obj': file_obj, upload_storage: upload_storage}
    return Cargo(error_code, exception_error, next, cargo.final)


# eof

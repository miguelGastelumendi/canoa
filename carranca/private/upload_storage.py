# Equipe da Canoa -- 2024
#
# mgd
# cSpell:ignore
"""
Upload File Path Configurations
see README.md
Part of Canoa `File Validation` Processes
"""
from os import path
from ..helpers.py_helper import path_remove_last

class UploadStorage():
    class _Folder:
        # names are from the point of view of data_validate
        validate_output = 'report' #data_validate writes is output here
        validate_input = 'data'
        # this is a shared folder
        data_tunnel = 'data_tunnel'
        # this is a local folder to keep all uploaded_file
        uploaded_files = 'uploaded_files'

    class _Path:
        def __init__(self, user_code, app_config):
            """ Parent folder of both: canoa & data_validate """
            _common = path_remove_last(app_config.ROOT_FOLDER)
            """ Path to uploaded files canoa\uploaded_files """
            self.uploaded_files = path.join(('.' if _common == None else _common), UploadStorage.Folders.uploaded_files)
            inter_common = path_remove_last(_common)
            """ Path to a common folder to be used by both apps canoa & data_validate """
            self.data_tunnel = path.join(inter_common, UploadStorage.Folders.data_tunnel)
            """ Path where the user's zip file is extracted """
            self.data_tunnel_user_write = path.join(self.data_tunnel, user_code, UploadStorage.Folders.validate_input)
            """ Path where the data_validate write the report """
            self.data_tunnel_user_read = path.join(self.data_tunnel, user_code, UploadStorage.Folders.validate_output)

    def __init__(self, user_code, app_config, file_name):
        self.app_config = app_config
        self.user_code = user_code
        self.path = self._Path(user_code, app_config)
        self.folder = self._Folder() # not really needed, but
        self.file_name = file_name


#eof






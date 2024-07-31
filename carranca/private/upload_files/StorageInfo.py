"""
    Upload Storage (File, Path structure) Information

    see README.md
    Part of Canoa `File Validation` Processes

    Equipe da Canoa -- 2024
    mgd
"""
# cSpell:ignore

from os import path
from ...helpers.file_helper import path_remove_last

class StorageInfo:
    """
    Upload File Path Configurations, Folders and
    file name see README.md
    """

    class _Folder:
        # names are from the point of view of ''data_validate''
        validate_output = 'report'  # 'data_validate' writes is output here
        validate_input = 'data'     # reads input (unzip files) from here
        # this is a shared folder
        data_tunnel = 'data_tunnel'
        # this is a local folder to keep all uploaded_file
        uploaded_files = 'uploaded_files'

    class _Path:
        def __init__(self, user_folder: str, common_folder: str, data_validate_folder: str, batch_name: str):
            # Path to uploaded files canoa/uploaded_files
            uploaded_files = path.join(
                ('.' if common_folder is None else common_folder),
                StorageInfo._Folder.uploaded_files,
            )
            # Path to all user files are kept
            self.user = path.join(uploaded_files, user_folder)
            # Path to the patent folder off both apps: canoa and data_validate
            self.apps_parent_path = path_remove_last(common_folder)

            # Path to a data_validate app
            data_tunnel = path.join(
                self.apps_parent_path, StorageInfo._Folder.data_tunnel
            )
            # Path to a common folder to be used by both apps canoa & data_validate
            data_tunnel = path.join(
                self.apps_parent_path, StorageInfo._Folder.data_tunnel
            )
            # Path where the user's zip file is extracted
            self.data_tunnel_user_write = path.join(
                data_tunnel, user_folder, StorageInfo._Folder.validate_input
            )
            # Path where the data_validate write the report
            self.data_tunnel_user_read = path.join(
                data_tunnel, user_folder, StorageInfo._Folder.validate_output
            )
            # External batch origin (copy from here if not exists or is newer)
            self.batch_source_name = path.join(common_folder, batch_name)

            # External batch that calls `data_validate` with arguments (see submit.py)
            self.batch_full_name = path.join(data_tunnel, batch_name)

            # External batch origin (copy from here if not exists or newer)
            self.data_validate = path.join(self.apps_parent_path, data_validate_folder)


    def __init__(self, user_folder: str, common_folder: str, data_validate_folder: str, batch_name: str):
        self._user_folder = user_folder
        self.path = self._Path(user_folder, common_folder, data_validate_folder, batch_name)
        self.folder = self._Folder()  # not really needed, but conventions.
        # values are given during the process
        self.uploaded_file_name = ''
        self.uploaded_original_name = None
        self.user_file_name = ''

    def user_file_full_name(self):
        return path.join(self.path.user, self.user_file_name)

# eof

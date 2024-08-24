"""
    Upload Storage (File, Path structure) Information

    see README.md
    Part of Canoa `File Validation` Processes

    Equipe da Canoa -- 2024
    mgd
"""

# cSpell:ignore

from os import path
from ...helpers.file_helper import path_remove_last_folder


class StorageInfo:
    """
    Received (upload | download) File Path Configurations, Folders and
    file name see README.md
    """

    class _User:
        def __init__(
            self,
            downloaded: str,
            uploaded: str,
            folder: str,
        ):
            self.downloaded = path.join(downloaded, folder)
            self.uploaded = path.join(uploaded, folder)
            self.folder = folder

    class _Folder:
        # names are from the point of view of ''data_validate''
        validate_output = "report"  # 'data_validate' writes is output here
        validate_input = "data"  # reads input (unzip files) from here
        # this is a shared folder
        data_tunnel = "data_tunnel"
        # this is a local folder to keep all uploaded files
        uploaded_files = "uploaded"
        # this is a local folder to keep all downloaded files
        downloaded_files = "downloaded"
        # this is a local for uploaded, downloaded & others users files
        user_files = "user_files"

    class _Path:
        def __init__(
            self,
            parent,
            user_folder: str,
            common_folder: str,
            data_validate_folder: str,
            batch_name: str,
        ):

            def _common_user_folder(folder: str):
                return path.join(
                    ("." if common_folder is None else common_folder),
                    StorageInfo._Folder.user_files,
                    folder,
                )

            # Path to all user's files are kept
            self.user = StorageInfo._User(
                _common_user_folder(StorageInfo._Folder.downloaded_files),
                _common_user_folder(StorageInfo._Folder.uploaded_files),
                user_folder,
            )

            self.working_folder = (
                self.user.downloaded if parent.file_was_downloaded else self.user.uploaded
            )

            # Path to the patent folder off both apps: canoa and data_validate
            self.apps_parent_path = path_remove_last_folder(common_folder)

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

    def __init__(
        self,
        user_folder: str,
        common_folder: str,
        data_validate_folder: str,
        batch_name: str,
        file_was_downloaded: bool,
    ):
        self._user_folder = user_folder
        self.folder = self._Folder()  # not really needed, but conventions.
        self.file_was_downloaded = file_was_downloaded
        self.file_was_uploaded = not file_was_downloaded
        self.path = self._Path(
            self, user_folder, common_folder, data_validate_folder, batch_name
        )

        # values are given during the process
        self.received_file_name = ""
        self.received_original_name = None
        self.working_file_name = ""

    def working_file_full_name(self):
        return path.join(self.path.working_folder, self.working_file_name)


# eof

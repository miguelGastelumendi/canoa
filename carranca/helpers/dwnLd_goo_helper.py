# Equipe da Canoa -- 2024
# Files Download: Google Drive (except zip) & others Publicly Shared Files
#
# inspired in
# https://stackoverflow.com/questions/38511444/python-download-files-from-google-drive-using-url
# mgd 2024-08-01

# cSpell:ignore puremagic surl googleapiclient gserviceaccount chunksize

import requests
import puremagic
import urllib.parse
from os import path, remove, rename
#from zlib import crc32

from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials


from ..shared import app_config, app_log
from .py_helper import is_str_none_or_empty, to_str
from .file_helper import is_same_file_name, change_file_ext, path_remove_last_folder


def is_url_valid(url: str) -> bool:
    try:
        urllib.parse.urlparse(url)
        return True
    except:
        return False


def is_gd_url_valid(url: str) -> int:
    result = 0
    if is_str_none_or_empty(url) or len(url) < 10:
        result = 1
    elif not url.lower().startswith("https://"):
        result = 2
    elif not is_url_valid(url):
        result = 3
    else:
        file_id = get_file_id_from_url(url)
        if file_id == None:
            result = 4
        elif not file_id.replace("_", "u").isalnum():
            result = 5
    return result


def get_file_id_from_url(url: str) -> str:
    """Extracts the file ID from a Google Drive shared link."""
    id = None
    surl = to_str(url)
    parts = surl.split("/")
    if len(parts) < 3:
        return None
    try:
        id = parts[parts.index("d") + 1]
    except ValueError:
        id = None  # || pass

    if id is None:
        from urllib.parse import urlparse, parse_qs

        purl = urlparse(surl)
        qs = parse_qs(purl)
        id = qs["id"]

    return id


def download_response(
    response: requests.Response, filename: str, rename_it: bool
) -> int:

    task_code = 1
    _, file_ext = path.splitext(filename)
    task_code = 2
    try:
        ext_found = not rename_it
        ext_by_magic = None
        with open(filename, "wb") as f:
            task_code = 4
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive new chunks
                    task_code = 6
                    f.write(chunk)
                    task_code = 8
                    ext_by_magic = (
                        ext_by_magic if ext_found else puremagic.what(None, chunk)
                    )
                    ext_found = ext_found or bool(
                        ext_by_magic
                    )  # just try to find extension with the first `chunk`

        if rename_it and not is_same_file_name(to_str(ext_by_magic), file_ext):
            task_code = 9
            new_filename = change_file_ext(filename, ext_by_magic)
            rename(filename, new_filename)

        return 0
    except Exception as e:
        #   app_log.error(f"Could save file  [{filename}], error [{e}].")
        return task_code


def download_public_google_file(
    url_or_file_id: str,
    file_folder: str,
    del_file_if_exists: bool = True,
    debug: bool = False,
) -> tuple[int, str]:
    """Downloads a public Google file.
    Args:
        url_or_file_id: The URL or file ID of the Google file.
        file_folder: The folder where the downloaded file should be saved.
        del_file_if_exists: Whether to delete the file if it already exists in the folder.

    Returns:
        A tuple containing:
            - The error code (0 if successful, non-zero if an error occurred).
            - The name of the downloaded file.
    """

    def get_file_metadata(service, file_id):
        file_md = service.files().get(fileId=file_id).execute()
        return file_md

    task_code = 1
    file_name = None
    file_md = None
    try:
        # Get file_id
        file_id = None
        if is_str_none_or_empty(url_or_file_id) or len(url_or_file_id) < 10:
            task_code = 2
            raise ValueError(
                f"Invalid parameter value 'url_or_file_id' [{url_or_file_id}]]."
            )
        elif url_or_file_id.lower().startswith("https://"):
            task_code = 3
            file_id = get_file_id_from_url(url_or_file_id)
        else:
            file_id = url_or_file_id

        if not file_id.replace("_", "u").isalnum():
            task_code = 4
            raise ValueError(f"Invalid value for file_id [{file_id}].")
        elif not path.isdir(file_folder):
            task_code = 5
            raise ValueError(f"Invalid value for file_id [{file_id}].")
        else:
            task_code = 6

        #  email: canoa-download@satelier-canoa.iam.gserviceaccount.com
        scope = ["https://www.googleapis.com/auth/drive.readonly"]

        # TODO: Pass as param
        service_account_file = path.join(
            path_remove_last_folder(app_config.ROOT_FOLDER),
            "LocalDrive",
            "canoa-download-key.json",
        )

        task_code += 1
        if not path.isfile(service_account_file):
            raise FileNotFoundError(service_account_file)

        task_code += 1
        credentials = Credentials.from_service_account_file(
            service_account_file, scopes=scope
        )

        task_code += 1
        service = build("drive", "v3", credentials=credentials)

        task_code += 1
        file_md = get_file_metadata(service, file_id)

        task_code += 1
        file_name = file_md["name"]
        file_full_path = path.join(file_folder, file_name)

        if not path.isfile(file_full_path):
            pass
        elif del_file_if_exists:
            #############
            if app_config.DEBUG:
                app_log.error("Keeping file in debug mode!")
                return 0, file_name, None
            #############


            task_code += 1
            remove(file_full_path)
            if path.isfile(file_full_path):
                PermissionError(file_full_path)
        else:
            task_code += 2
            FileExistsError(file_full_path)

        task_code += 3
        request = service.files().get_media(fileId=file_id)

        task_code += 1
        with open(file_full_path, "wb") as f:
            task_code += 1
            cs = int(0 if not debug else 2 * 1024 * 1024)  # 2MB
            downloader = MediaIoBaseDownload(f, request, chunksize=cs)
            task_code += 1
            done = False
            app_log.debug(f"Download of file {file_full_path} started.")
            # file_crc32 = crc32(b'')  # Initialize CRC32 checksum
            while done is False:
                status, done = downloader.next_chunk()
                # TODO find how: file_crc32 = crc32(status, file_crc32)
                app_log.debug("Downloaded %d%%." % int(status.progress() * 100))

        task_code = 0
    except Exception as e:
        msg_error = f"An error ocurred while downloading the file. Task code {task_code}, message '{e}'.)"
        app_log.error(msg_error, exc_info=task_code)

    return task_code, file_name, file_md


# if __name__ == "__main__":
#     url = "https://drive.google.com/file/d/1H0BfjYJrf0p_ehqDoUH0wXIJzbAXwUKd/view?usp=sharing"
#     download_public_google_file(url, "./uploaded_files/")


# eof

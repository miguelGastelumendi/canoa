"""
User's Received Files's Management

    Fetch one record (by id) or all records for a user_id

Equipe da Canoa -- 2025
mgd 2025-01-14 & 03-18
"""

from os import path
from typing import Tuple
from ..models import ReceivedFiles
from ...common.app_context_vars import logged_user
from ...config.ValidateProcessConfig import ValidateProcessConfig

from ...helpers.db_helper import DBRecords
from ...helpers.user_helper import UserFolders
from ...helpers.file_helper import change_file_ext


def fetch_record_s(no_sep: str, rec_id: int = None, user_id: int = None) -> Tuple[DBRecords, str, str]:
    """Fetch received files records from the view vw_user_data_files

    no_sep: str: text to show when the record has an empty SEP
    rec_id: int | None: record id to fetch or None
            When rec_id is:
                - None, fetch all records for the user (user_id or logged_user)
                - has value, ignore user_id and fetch the record with the given id & return file full_name too
    user_id: int | None user id to fetch records for
            When user_id:
                - None, fetch records for the logged user
    return: DBRecords: records fetched and the last record's file full_name

    """

    if user_id is None:
        user_id = logged_user.id if logged_user else None

    if rec_id is None and user_id is None:
        return DBRecords(), None, None

    received_files = ReceivedFiles.get_records(id=rec_id, user_id=user_id)
    received_rows = DBRecords(received_files.table_name)
    file_full_name: str = None
    report_ext = ValidateProcessConfig(False).output_file.ext

    if received_files:
        """Adapt the records to the local environment"""
        uf = UserFolders()

        for record in received_files:
            folder = uf.uploaded if record.file_origin == "L" else uf.downloaded
            file_full_name = path.join(folder, logged_user.folder, record.stored_file_name)
            # Copy specific fields to a new object 'row'
            row = {
                "id": record.id,
                "data_f_found": path.isfile(file_full_name),  # data_file was found
                "report_found": path.isfile(change_file_ext(file_full_name, report_ext)),
                "sep": record.sep_fullname if record.sep_fullname else no_sep,
                "file_name": change_file_ext(record.file_name),
                "user_name": record.user_name,
                "receipt": record.user_receipt,
                "when": record.submitted_at,
                "errors": record.report_errors,
                "warns": record.report_warns,
            }
            received_rows.append(row)

    return received_rows, file_full_name, report_ext


# eof

"""
User's Received Files's Management

    Fetch a list of users with the number
    of received files and other attributes.

Equipe da Canoa -- 2025
mgd 2025-01-14 & 03-18
"""

from ..models import ReceivedFilesCount
from ...common.app_context_vars import logged_user

from ...helpers.db_helper import DBRecords


def fetch_user_s(user_id: int = None) -> DBRecords:
    """
    user_id:
        if None: fetch all users name, email ...
        else: a record with the count of received files for the user_id.
    """
    if user_id is not None:
        # read one record
        pass
    elif logged_user.is_power if logged_user else False:
        # read all records
        user_id = None
    else:
        return DBRecords()

    received_files_count = ReceivedFilesCount.get_records(user_id)
    received_rows = DBRecords(received_files_count.table_name, received_files_count)
    # if received_files_count:
    #     for record in received_files_count:
    #         row = {
    #             "user_id": record.user_id,
    #             "user_name": record.user_name,
    #             "user_email": record.user_email,
    #             "rol_id": record.rol_id,
    #             "rol_name": record.rol_name,
    #             "rol_abbr": record.rol_abbr,
    #             "files_count": record.files_count,
    #         }
    #         received_rows.append(row)

    return received_rows


# eof

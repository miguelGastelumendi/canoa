"""
User's Received Files's Management

    Fetch a list of users with the number
    of received files and other attributes.

Equipe da Canoa -- 2025
mgd 2025-01-14 & 03-18
"""

from ..models import ReceivedFilesCount
from ...common.app_context_vars import app_user

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
    elif app_user.is_power if app_user else False:
        # read all records
        user_id = None
    else:
        return DBRecords()

    received_files_count = ReceivedFilesCount.get_records(user_id)
    received_rows = DBRecords(received_files_count.table_name, received_files_count)

    return received_rows


# eof

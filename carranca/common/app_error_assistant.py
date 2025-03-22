"""
    *App Error Helpers*

    - Error Codes, per 'module'
    - Error Flags
    - Exception

Equipe da Canoa  2024 — 2025
mgd
"""

# cSpell:ignore mgmt

from enum import IntEnum


def did_I_stumbled(e: Exception):
    """Is it me who stumbled?"""
    return isinstance(e, CanoeStumbled)


class CanoeStumbled(Exception):
    """A specialized Exception for Canoa"""

    def __init__(self, msg: str, error_code: int = 0, is_fatal: bool = False):
        self.msg = msg
        self.error_code = error_code
        self.is_fatal = is_fatal

    def __str__(self):
        return f"{self.msg} (Error Code: {self.error_code}, Fatal: {self.is_fatal})"


class ModuleErrorCode(IntEnum):
    # Public Access Control Processes
    ACCESS_CONTROL_LOGIN = 100  # 1-14
    ACCESS_CONTROL_REGISTER = 120  # 1-06
    ACCESS_CONTROL_PW_CHANGE = 130  # 1-08
    ACCESS_CONTROL_PW_RECOVERY = 140
    ACCESS_CONTROL_PW_RESET = 160

    # User Interface Text Retrieval
    UI_TEXTS = 170  # 1

    # RECEIVE_FILE_* =: [200... 270] + 100
    RECEIVE_FILE_ADMIT = 200
    RECEIVE_FILE_CHECK = 210
    RECEIVE_FILE_REGISTER = 230
    RECEIVE_FILE_UNZIP = 240
    RECEIVE_FILE_SUBMIT = 250
    RECEIVE_FILE_EMAIL = 260
    RECEIVE_FILE_PROCESS = 270
    RECEIVE_FILE_EXCEPTION = 100  # this is added, as an exception, process.py

    NEXT_MODULE_ERROR = 400

    SEP_EDIT = 500
    SEP_MGMT = 550

    RECEIVED_FILES_MGMT = 600


class RaiseIf:
    """Flags to raise an error if
    or just ignore the condition
    """

    ignite_no_sql_conn = True
    no_ui_texts = True


# eof

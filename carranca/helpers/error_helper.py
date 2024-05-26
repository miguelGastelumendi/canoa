# Equipe da Canoa -- 2024
# helpers\error_helper.py
#
# mgd
# cSpell:ignore
"""
    *Error constants enum*
"""


from enum import IntEnum

class ModuleErrorCode(IntEnum):
    # public
    PASSWORD_RECOVERY = 110
    PASSWORD_RESET = 120

    # UPLOAD_FILE_* =: [200... 270] + 100
    UPLOAD_FILE_CHECK = 200
    UPLOAD_FILE_REGISTER = 220
    UPLOAD_FILE_UNZIP = 230
    UPLOAD_FILE_SUBMIT = 240
    UPLOAD_FILE_EMAIL = 250
    UPLOAD_FILE_PROCESS = 260
    UPLOAD_FILE_EXCEPTION = 100 # this is added, as an exception, process.py

    NEXT_MODULE_ERROR  = 400

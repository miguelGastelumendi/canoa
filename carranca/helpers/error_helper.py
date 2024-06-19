"""
*Error constants enum*

Equipe da Canoa -- 2024
mgd
"""
# cSpell:ignore

from enum import IntEnum

class ModuleErrorCode(IntEnum):
    # Public Access Control Processes
    ACCESS_CONTROL_LOGIN = 100        #1-14
    ACCESS_CONTROL_REGISTER = 120     #1-06
    ACCESS_CONTROL_PW_CHANGE = 130    #1-08
    ACCESS_CONTROL_PW_RECOVERY = 140
    ACCESS_CONTROL_PW_RESET = 160

    # UPLOAD_FILE_* =: [200... 270] + 100
    UPLOAD_FILE_CHECK = 200
    UPLOAD_FILE_REGISTER = 220
    UPLOAD_FILE_UNZIP = 230
    UPLOAD_FILE_SUBMIT = 240
    UPLOAD_FILE_EMAIL = 250
    UPLOAD_FILE_PROCESS = 260
    UPLOAD_FILE_EXCEPTION = 100 # this is added, as an exception, process.py

    NEXT_MODULE_ERROR  = 400

# eof
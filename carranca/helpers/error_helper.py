# Equipe da Canoa -- 2024
# helpers\error_helper.py
#
# mgd
# cSpell:ignore
"""
    *Error constants List*
"""


from enum import Enum

class ModuleErrorCode(Enum):
    # public
    PASSWORD_RECOVERY = 110
    PASSWORD_RESET = 120
    UPLOAD_FILE_CHECK = 130

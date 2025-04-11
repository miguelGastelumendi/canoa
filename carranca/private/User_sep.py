"""
 Basic information of a user SEP

Equipe da Canoa -- 2024
mgd
"""

# cSpell:ignore MgmtSep


from os import path
from ..helpers.py_helper import is_str_none_or_empty


# User SEP info
class UserSEP:
    # from .models import MgmtSep
    def __init__(self, icon_url: str, sep_fullname: str, sep):  # :MgmtSep):
        from .SepIconConfig import SepIconConfig

        local_path = SepIconConfig.local_path
        self.id = sep.id
        self.icon_url = icon_url
        self.full_name = sep_fullname
        self.has_icon = not is_str_none_or_empty(sep.icon_file_name)
        self.icon_file_name = sep.icon_file_name
        self.icon_full_name = path.join(local_path, sep.icon_file_name) if self.has_icon else ""


# eof

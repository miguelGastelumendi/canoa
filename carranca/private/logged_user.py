"""
    *logged_user*

    Has what flask's `current_user` offers plus Canoa utilities

    Equipe da Canoa -- 2024
    mgd
"""

# cSpell:ignore MgmtSep


# Basic information of the logged user.
class UserSEP:
    # from .models import MgmtSep
    def __init__(self, local_path, url, sep_fullname, sep):  # MgmtSep):
        from ..helpers.py_helper import is_str_none_or_empty
        from os import path

        self.id = sep.id
        self.icon_url = url
        self.full_name = sep_fullname
        self.has_icon = not is_str_none_or_empty(sep.icon_file_name)
        self.icon_file_name = sep.icon_file_name
        self.icon_full_name = path.join(local_path, sep.icon_file_name) if self.has_icon else ""


class LoggedUser:
    def __init__(self):
        from flask_login import current_user
        from .SepIconConfig import SepIconConfig
        from .sep_icon import icon_prepare_for_html
        from ..helpers.user_helper import get_user_code, get_user_folder
        from ..app_request_scoped_vars import sidekick

        self.ready = current_user is not None

        if not self.ready:
            sidekick.display.debug(f"{self.__class__.__name__} was reset.")
            self.name = "?"
            self.id = -1
            self.email = ""
            self.code = "0"
            self.path = ""
            self.sep = None
        else:
            sidekick.display.debug(f"{self.__class__.__name__} was created.")
            self.name = current_user.username
            self.id = current_user.id
            self.email = current_user.email
            self.code = get_user_code(current_user.id)
            self.folder = get_user_folder(current_user.id)
            self.path = SepIconConfig.local_path
            url, sep_fullname, sep = (
                (None, None, None)
                if current_user.mgmt_sep_id is None
                else icon_prepare_for_html(current_user.mgmt_sep_id)
            )
            self.sep = None if sep is None else UserSEP(self.path, url, sep_fullname, sep)

    def __repr__(self):
        info = "Unknown" if not self.ready else f"{self.name} [{self.id}]"
        return f"<{self.__class__.__name__}({info})>"


# eof

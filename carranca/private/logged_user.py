"""
Module for handling logged user information.

This module extends Flask's `current_user` with additional utilities specific to Canoa.

Equipe da Canoa -- 2024
mgd
"""

# cSpell:ignore MgmtSep mgmt

from os import path
from flask_login import current_user
from werkzeug.local import LocalProxy

from ..helpers.py_helper import is_str_none_or_empty
from ..helpers.user_helper import get_user_code, get_user_folder
from ..common.app_constants import app_lang


# Basic information of the logged user.
class UserSEP:
    # from .models import MgmtSep
    def __init__(self, local_path, url, sep_fullname, sep):  # MgmtSep):
        self.id = sep.id
        self.icon_url = url
        self.full_name = sep_fullname
        self.has_icon = not is_str_none_or_empty(sep.icon_file_name)
        self.icon_file_name = sep.icon_file_name
        self.icon_full_name = path.join(local_path, sep.icon_file_name) if self.has_icon else ""


class LoggedUser:
    def __init__(self):
        from .SepIconConfig import SepIconConfig
        from .user_roles import Roles
        from ..common.app_context_vars import sidekick

        self.ready = current_user.is_authenticated if current_user else False

        if not self.ready:
            sidekick.display.debug(f"{self.__class__.__name__} was reset.")
            self.lang = app_lang  # TODO: None -> use Browser default
            self.name = "?"
            self.id = -1
            self.email = ""
            self.code = "0"
            self.path = ""
            self.sep = None
            self.role = Roles.Unknown
        else:
            from .sep_icon import icon_prepare_for_html

            sidekick.display.debug(f"{self.__class__.__name__} was created.")
            self.lang = current_user.lang
            self.name = current_user.username
            self.id = current_user.id
            self.email = current_user.email
            self.code = get_user_code(current_user.id)
            self.folder = get_user_folder(current_user.id)
            self.path = SepIconConfig.local_path
            self.role = Roles.Unknown
            self.isAdm = False
            # ROLE self.role = Roles.Admin
            if current_user.mgmt_sep_id is None:
                self.sep = None
            else:  # TODO improve performance with cache (maybe session)

                def load_sep():
                    url, sep_fullname, sep = icon_prepare_for_html(current_user.mgmt_sep_id)
                    return UserSEP(self.path, url, sep_fullname, sep)

                self.sep = LocalProxy(load_sep)

    def __repr__(self):
        user_info = "Unknown" if not self.ready else f"{self.name} [{self.id}]"
        return f"<{self.__class__.__name__}({user_info})>"


# eof

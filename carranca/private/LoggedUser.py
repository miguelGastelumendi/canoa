"""
Class for handling logged user information.

This module extends Flask's `current_user` with additional utilities specific to Canoa.

Equipe da Canoa -- 2024
mgd
"""

# cSpell:ignore MgmtSep mgmt

from flask_login import current_user

# from werkzeug.local import LocalProxy

from .roles_abbr import RolesAbbr
from common.app_constants import APP_LANG
from ..helpers.user_helper import get_user_code, get_user_folder


# Basic information of the logged user.
class LoggedUser:
    def __init__(self):
        from ..common.app_context_vars import sidekick
        from .SepIconConfig import SepIconConfig  # Avoid Circular 2025.02.20

        self.ready = current_user.is_authenticated if current_user else False

        if not self.ready:
            sidekick.display.debug(f"{self.__class__.__name__} was reset.")
            self.lang = APP_LANG  # TODO: None -> use Browser default
            self.name = "?"
            self.id = -1
            self.email = ""
            self.code = "0"
            self.folder = ""
            self.path = ""
            self.role_abbr = None
            self.role_name = None
            self.sep = None
            self.is_adm = False
            self.is_power = False
        else:
            sidekick.display.debug(f"{self.__class__.__name__} was created.")
            self.lang = current_user.lang
            self.name = current_user.username
            self.id = current_user.id
            self.email = current_user.email
            self.code = get_user_code(current_user.id)
            self.folder = get_user_folder(current_user.id)
            self.path = SepIconConfig.local_path
            self.role_abbr: str = current_user.role.abbr
            self.role_name: str = current_user.role.name
            self.is_adm: bool = self.role_abbr == RolesAbbr.Admin.value
            self.is_power: bool = self.is_adm or (
                (self.role_abbr == RolesAbbr.Suporte.value) and sidekick.debugging
            )

    @property
    def sep(self):
        if current_user.mgmt_sep_id is None:
            return None
        else:
            from ..common.app_context_vars import user_sep

            return user_sep

            # from .sep_icon import icon_prepare_for_html

            # TODO improve performance with cache (maybe session)
            # def load_sep():
            #     url, sep_fullname, sep = icon_prepare_for_html(current_user.mgmt_sep_id)
            #     return UserSEP(self.path, url, sep_fullname, sep)

            # self.sep = LocalProxy(load_sep)

    def __repr__(self):
        user_info = "Unknown" if not self.ready else f"{self.name} [{self.id}]"
        return f"<{self.__class__.__name__}({user_info})>"


# eof

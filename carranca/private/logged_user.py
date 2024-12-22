"""
    *logged_user*

    Has what flask's `current_user` offers plus Canoa utilities

    Equipe da Canoa -- 2024
    mgd
"""

# cSpell:ignore mgmt
from werkzeug.local import LocalProxy

# see sidekick.py for a (nice) explanation of this 'variables':
_logged_user = None
logged_user = LocalProxy(lambda: _get_logged_user())


def _get_logged_user():
    # copied from ?\canoa\.venv\Lib\site-packages\flask_login\utils.py
    from flask import has_request_context, g
    from flask_login import current_user
    from ..helpers.pw_helper import is_someone_logged

    global _logged_user

    def _bring_it():
        global _logged_user
        if _logged_user is None:
            _logged_user = LoggedUser(current_user)
        return _logged_user

    if not is_someone_logged():
        return None

    elif not has_request_context():
        return None

    elif "_logged_user" not in g:
        g._logged_user = _bring_it()

    else:
        _logged_user = g._logged_user

    return _logged_user


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
    def __init__(self, c_user):
        from .SepIconConfig import SepIconConfig
        from .sep_icon import icon_prepare_for_html
        from ..helpers.user_helper import get_user_code, get_user_folder
        from ..Sidekick import sidekick

        sidekick.display.debug(f"{self.__class__.__name__} was created.")
        self.ready = c_user is not None

        if not self.ready:
            self.name = "?"
            self.id = -1
            self.email = ""
            self.code = "0"
            self.path = ""
            self.sep = None
        else:
            self.name = c_user.username
            self.id = c_user.id
            self.email = c_user.email
            self.code = get_user_code(c_user.id)
            self.folder = get_user_folder(c_user.id)
            self.path = SepIconConfig.local_path
            url, sep_fullname, sep = (
                (None, None, None)
                if c_user.mgmt_sep_id is None
                else icon_prepare_for_html(c_user.mgmt_sep_id)
            )
            self.sep = None if sep is None else UserSEP(self.path, url, sep_fullname, sep)


# eof

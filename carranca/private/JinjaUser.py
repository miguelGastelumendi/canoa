"""
Class for handling the 'jinja user' (seen in *.j2 files) information.

This class shrinks the amount of information that is passed to the Jinja2 templates.

Equipe da Canoa -- 2025
mgd
"""

# cSpell:ignore

from common.app_constants import APP_LANG
from .LoggedUser import LoggedUser


class JinjaUser:
    def __init__(self, logged_user: LoggedUser):
        from ..common.app_context_vars import sidekick

        self.ready = logged_user.ready if logged_user else False

        if self.ready:
            sidekick.display.debug(f"{self.__class__.__name__} was created.")
            self.lang = logged_user.lang
            self.name = logged_user.name
        else:
            sidekick.display.debug(f"{self.__class__.__name__} was reset.")
            self.lang = (
                APP_LANG  # locale.getdefaultlocale()[0]  # TODO, check if available
            )
            self.name = "?"

    def __repr__(self):
        user_info = "Unknown" if not self.ready else f"{self.name} [{self.lang}]"
        return f"<{self.__class__.__name__}({user_info})>"


# eof

"""
Class for handling logged user SEPs information.

See AppUser.seps: List[UserSEP]

Equipe da Canoa -- 2025
mgd
"""

# spell:ignore Mgmt

from typing import TypeAlias, Optional, List, Dict, Any
from ..helpers.py_helper import to_base
from ..helpers.types_helper import error_message

user_sep_list: TypeAlias = List["UserSep"]
user_sep_dict: TypeAlias = Dict[str, Any]
user_seps_rtn: TypeAlias = user_sep_list | error_message


class UserSep:
    """
    Contains UI-related information for each SEP.
    This class is resource-intensive to instantiate
    due to the 'icon_url' attribute, which ensures
    that an icon file is available at the specified URL.
    If the icon file is missing, it will be created.

    see .models.MgmtUserSeps
    """

    base: int = 13

    @staticmethod
    def to_id(code: str) -> int:
        try:
            id = int(int(code, UserSep.base) / UserSep.base)
        except:
            id = -1
        return id

    @property
    def code(self) -> str:
        return to_base(UserSep.base * self.id, UserSep.base)  # ;-)

    def __init__(
        self,
        id: int,
        fullname: str,
        description: str,
        visible: bool,
        icon_file_name: str,
        icon_url: Optional[str] = None,
    ):
        self.id = id
        self.fullname = fullname
        self.description = description
        self.visible = visible
        self.icon_file_name = icon_file_name
        self.icon_url = icon_url

    id: int
    fullname: str
    description: str
    visible: bool
    icon_file_name: str
    icon_url: Optional[str]  # expensive to 'calculate'


# eof

"""
SEP Icon
Prepares the SEP's Icon for HTML

Equipe da Canoa -- 2024
mgd 2024-11-16
"""

# cSpell:ignore mgmt

from os import path, remove
from typing import Optional, Tuple

from ..helpers.py_helper import is_str_none_or_empty
from ..helpers.file_helper import folder_must_exist
from ..common.app_context_vars import sidekick

from .models import MgmtSep
from .SepIcon import SepIcon, IgniteSepIcon
from .SepIconConfig import SepIconConfig


def icon_refresh(sep: SepIcon | MgmtSep) -> bool:

    refreshed = False
    if is_str_none_or_empty(sep.icon_file_name):
        return refreshed

    try:
        if path.isfile(sep.icon_full_name):
            remove(sep.icon_full_name)

        icon_prepare_for_html(sep.id)
        refreshed = True
    except:
        pass  # not a terrible bug, later will be refreshed

    return refreshed


def icon_prepare_for_html(sep_or_id: Optional[MgmtSep | int]) -> IgniteSepIcon:
    """
    Creates a file with the SEP's svg data (if necessary) and
    returns
        url of the icon_file (can be to 'no_file')
        , full name of the sep (schema/sep)
        , sep record
    """

    if sep_or_id is None:
        sep, sep_fullname = (None, "")
        icon_file_name = SepIconConfig.none_file
    else:
        sep, sep_fullname = MgmtSep.get_sep(sep_or_id) if isinstance(sep_or_id, int) else (sep_or_id, "")
        icon_file_name = SepIconConfig.error_file if sep is None else sep.icon_file_name

    no_file = is_str_none_or_empty(icon_file_name)
    file_name = SepIconConfig.empty_file if no_file else icon_file_name

    file_full_name = path.join(SepIconConfig.local_path, file_name)
    icon_url = SepIconConfig.set_url(file_name)

    if not folder_must_exist(SepIconConfig.local_path):
        # TODO: express this error more clearly
        sidekick.display.error(f"Cannot create folder [{SepIconConfig.local_path}]")
        return "", "", sep
    elif path.isfile(file_full_name):
        pass
    else:
        match icon_file_name:
            case SepIconConfig.error_file:
                content = SepIconConfig.error_content()
            case SepIconConfig.empty_file:
                content = SepIconConfig.empty_content()
            case SepIconConfig.none_file:
                content = SepIconConfig.none_content()
            case _:
                content = MgmtSep.icon_content(sep.id)

        with open(file_full_name, "w", encoding="utf-8") as file:
            file.write(content)

    initUserSEP = IgniteSepIcon(icon_url, sep_fullname, sep)

    return initUserSEP


# eof

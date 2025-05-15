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
from ..common.app_error_assistant import AppStumbled
from ..models.private import Sep, SchemaSEP

from .SepIcon import SepIcon, SepData
from .SepIconConfig import SepIconConfig


def icon_refresh(sep: SepIcon | Sep) -> bool:
    """
    /!\ This is can be resources heavy routine

    Deletes the icon file and recreates.
    """

    refreshed = False
    if is_str_none_or_empty(sep.icon_file_name):
        return refreshed

    try:
        file_full_name = SepIconConfig.get_local_name(sep.icon_file_name)
        if path.isfile(file_full_name):
            remove(file_full_name)

        do_icon_get_url(sep.id)
        refreshed = True
    except Exception as e:
        sidekick.display.error(f"Could not refresh icon [{file_full_name}].")

    return refreshed


# OBSOLETE
#
# def icon_prepare_for_html(sep_or_id: Optional[Sep | int]) -> SepData:
#     """
#     /!\ This is can be resources heavy routine

#     Creates a file with the SEP's svg data (if necessary) and
#     returns initUserSEP
#     """

#     if sep_or_id is None:
#         sep_id = None
#         sep, sep_fullname = (None, "")
#         icon_file_name = SepIconConfig.none_file
#     elif isinstance(sep_or_id, int):
#         sep_id: int = sep_or_id
#         sep, sep_fullname = Sep.get_sep(sep_id)
#         icon_file_name = SepIconConfig.error_file if sep is None else sep.icon_file_name
#     else:
#         sep: Sep = sep_or_id
#         sep_id: int = sep.id
#         sep_fullname = SchemaSEP.get_sep_fullname(sep_id)
#         icon_file_name = sep.icon_file_name

#     icon_url = do_icon_get_url(icon_file_name, sep_id)

#     sep_data = SepData(icon_url, sep_fullname, sep)
#     return sep_data


def do_icon_get_url(icon_file_name: str, sep_id: Optional[int] = None) -> str:
    """
    /!\ This is can be resources heavy routine

    Creates a file with the SEP's svg data (if necessary) and
    returns the file's url
    """

    if icon_file_name is None:
        icon_file_name = SepIconConfig.none_file
    elif icon_file_name == "":
        icon_file_name = SepIconConfig.empty_file

    file_full_name = SepIconConfig.get_local_name(icon_file_name)
    icon_url = SepIconConfig.get_icon_url(icon_file_name)

    if not folder_must_exist(SepIconConfig.local_path):
        # TODO: express this error more clearly
        sidekick.display.error(f"Cannot create folder [{SepIconConfig.local_path}]")
        return None
    elif not path.isfile(file_full_name):
        match icon_file_name:
            case SepIconConfig.error_file:
                content = SepIconConfig.error_content()
            case SepIconConfig.empty_file:
                content = SepIconConfig.empty_content()
            case SepIconConfig.none_file:
                content = SepIconConfig.none_content()
            case _:
                if sep_id == None:
                    content = SepIconConfig.none_content()
                else:
                    content, msg_error = Sep.get_content(sep_id)
                    if msg_error:
                        content = SepIconConfig.error_content()
                        sidekick.display.error(
                            f"Cannot retrieve icon content of SEP id {sep_id}': [{msg_error}]."
                        )

        try:
            with open(file_full_name, "w", encoding="utf-8") as file:
                file.write(content)
        except:
            raise AppStumbled(f"Error creating icon file [{file_full_name}].", 0)

    return icon_url


# eof

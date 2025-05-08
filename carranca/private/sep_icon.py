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
from ..helpers.types_helper import svg_content
from ..common.app_context_vars import sidekick

from .models import Sep
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
        file_full_name = path.join(SepIconConfig.local_path, sep.icon_file_name)
        if path.isfile(file_full_name):
            remove(file_full_name)

        icon_prepare_for_html(sep.id)
        refreshed = True
    except Exception as e:
        sidekick.display.error(f"Could not refresh icon [{file_full_name}].")

    return refreshed


def icon_prepare_for_html(sep_or_id: Optional[Sep | int]) -> SepData:
    """
    /!\ This is can be resources heavy routine

    Creates a file with the SEP's svg data (if necessary) and
    returns initUserSEP
    """

    if sep_or_id is None:
        sep_row, sep_fullname = (None, "")
        icon_file_name = SepIconConfig.none_file
    else:
        id_is_known = isinstance(sep_or_id, int)
        sep, id = (None, sep_or_id) if id_is_known else (sep_or_id, -1)
        sep_row, sep_fullname = Sep.get_sep(id if id_is_known else sep.id, False)
        icon_file_name = SepIconConfig.error_file if sep_row is None else sep_row.icon_file_name

    no_file = is_str_none_or_empty(icon_file_name)
    file_name = SepIconConfig.empty_file if no_file else icon_file_name

    file_full_name = path.join(SepIconConfig.local_path, file_name)
    icon_url = SepIconConfig.set_url(file_name)

    if not folder_must_exist(SepIconConfig.local_path):
        # TODO: express this error more clearly
        sidekick.display.error(f"Cannot create folder [{SepIconConfig.local_path}]")
        return SepData("", "", sep_row)
    elif not path.isfile(file_full_name):
        match icon_file_name:
            case SepIconConfig.error_file:
                content = SepIconConfig.error_content()
            case SepIconConfig.empty_file:
                content = SepIconConfig.empty_content()
            case SepIconConfig.none_file:
                content = SepIconConfig.none_content()
            case _:
                content, msg_error = Sep.get_content(sep_row.id)
                if msg_error:
                    content = SepIconConfig.error_content()
                    sidekick.display.error(
                        f"Cannot retrieve icon content of '{sep_row.name}': [{msg_error}]."
                    )

        with open(file_full_name, "w", encoding="utf-8") as file:
            file.write(content)

    sep_data = SepData(icon_url, sep_fullname, sep_row)

    return sep_data


# eof

"""
SEP Icon
Prepares the SEP's Icon for HTML

Equipe da Canoa -- 2024
mgd 2024-11-16
"""

# cSpell:ignore mgmt

from os import path, remove
from typing import Optional

from ..helpers.py_helper import is_str_none_or_empty
from ..helpers.file_helper import folder_must_exist
from ..common.app_context_vars import sidekick
from ..common.app_error_assistant import AppStumbled, JumpOut
from ..models.private import Sep

from .SepIcon import SepIcon, ICON_MIN_SIZE
from .SepIconMaker import SepIconMaker


def icon_refresh(sep: SepIcon | Sep) -> bool:
    """
    ⚠️ This is can be resources heavy routine

    Deletes the icon file and recreates.
    """

    refreshed = False
    if is_str_none_or_empty(sep.icon_file_name):
        return refreshed

    try:
        file_full_name = SepIconMaker.get_full_name(sep.icon_file_name)
        if path.isfile(file_full_name):
            remove(file_full_name)

        do_icon_get_url(sep.id)
        refreshed = True
    except Exception as e:

        sidekick.display.error(f"Could not refresh icon [{file_full_name}].")

    return refreshed


def icon_ready(file_full_name: str) -> bool:

    if not path.isfile(file_full_name):
        return False
    elif path.getsize(file_full_name) > ICON_MIN_SIZE:
        return True
    else:
        try:
            remove(file_full_name)
            return False
        except OSError as e:
            raise JumpOut(f"Error deleting file '{file_full_name}'.")


def do_icon_get_url(icon_file_name: str, sep_id: Optional[int] = None) -> str:
    """
    ⚠️ This is can be resources heavy routine

    Creates a file with the SEP's svg data (if necessary) and
    returns the file's url
    """

    if icon_file_name is None:
        icon_file_name = SepIconMaker.none_file
    elif icon_file_name == "":
        icon_file_name = SepIconMaker.empty_file

    file_full_name = SepIconMaker.get_full_name(icon_file_name)
    icon_url = SepIconMaker.get_url(icon_file_name)

    if not folder_must_exist(SepIconMaker.local_path):
        # TODO: express this error more clearly
        sidekick.display.error(f"Cannot create folder [{SepIconMaker.local_path}]")
        return None
    elif not icon_ready(file_full_name):
        content = ""
        match icon_file_name:
            case SepIconMaker.error_file:
                content = SepIconMaker.error_content
            case SepIconMaker.empty_file:
                content = SepIconMaker.empty_content
            case SepIconMaker.none_file:
                content = SepIconMaker.none_content
            case _:
                if sep_id is None:
                    content = SepIconMaker.none_content
                else:
                    content, msg_error = Sep.get_content(sep_id)
                    if msg_error:
                        content = SepIconMaker.error_content
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

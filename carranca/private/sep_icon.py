"""
    SEP Icon
    Prepares the SEP's Icon for HTML

    Equipe da Canoa -- 2024
    mgd 2024-11-16
"""

# cSpell:ignore mgmt

from os import path

from ..Sidekick import sidekick
from ..helpers.py_helper import is_str_none_or_empty
from ..helpers.file_helper import folder_must_exist

from .models import MgmtSep
from .SepIconConfig import SepIconConfig


def icon_prepare_for_html(sep_or_id: MgmtSep | int) -> str:
    """
    Creates a file with the SEP's file (if necessary) and
    returns the full path of the sep icon
    or to `SepIconConfig.empty_file` if None

    """
    sep, _ = MgmtSep.get_sep(sep_or_id) if isinstance(sep_or_id, int) else (sep_or_id, "")
    if sep is None:
        return None

    no_file = is_str_none_or_empty(sep.icon_file_name)
    file_name = SepIconConfig.empty_file if no_file else sep.icon_file_name
    file_full_name = path.join(SepIconConfig.path, file_name)
    url_file_name = SepIconConfig.set_url(file_name)

    if not folder_must_exist(SepIconConfig.path):
        # TODO set content, not url SepIconConfig.error_content
        sidekick.display.error(f"Cannot create folder [{SepIconConfig.path}]")
        return ""
    elif path.isfile(file_full_name):
        # Keep this code, just in case
        # with open(file_full_name, 'r', encoding='utf-8') as file:
        #     content = file.read()
        return url_file_name
    else:
        content = SepIconConfig.empty_content() if no_file else MgmtSep.get_sep_icon_content(sep.id)
        with open(file_full_name, "w", encoding="utf-8") as file:
            file.write(content)
        return url_file_name


# eof

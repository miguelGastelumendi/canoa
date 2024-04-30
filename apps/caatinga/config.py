"""
 config_caatinga.py
 ------------------

 The Caatinga Team
 mgd 2024-04-29

"""

from os import path
from apps.config import Config
from .pyHelper import to_base


class CaatingaConfig:
    _shift_id = 903
    _app_name = "Caatinga"
    folder_data = "user_data"
    folder_data = path.join(Config.basedir, _app_name, folder_data)
    folder_uploaded_files = path.join(folder_data, "uploaded_files")
    folder_html_docs = path.join(folder_data, "html_docs")
    """External user code """
    def user_code(id: int) -> str:
        return to_base(CaatingaConfig._shift_id + id, 12).zfill(4)

    def user_id(code: str) -> int:
        return from_base(code, 12) - CaatingaConfig._shift_id

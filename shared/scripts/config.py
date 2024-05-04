"""

 Equipe da Canoa -- 2024

 mgd 2024-04-29

"""

from os import path, makedirs
from carranca.config import Config
from .pyHelper import to_base, path_remove_last


class CarrancaConfig:
    _shift_id = 903
    # from 'frontEnd' -> .../Canoa/carranca
    folder_html_docs = path.join(Config.basedir, "html_docs")

    # shared scripts with data_validator
    _common = path_remove_last(Config.basedir)
    folder_shared = path.join(("." if _common == None else _common), "shared")
    folder_data = path.join(folder_shared,  "user_data")
    folder_uploaded_files = path.join(folder_data, "uploaded_files")

    # transitional data channel folder
    inter_common = path_remove_last(_common)
    folder_channel = path.join(inter_common, "data_channel")
    if not path.isdir(folder_channel):
        makedirs(folder_channel)


    email_originator = "assismauro@hotmail.com"

    """ External user code """
    def user_code(id: int) -> str:
        return to_base(CarrancaConfig._shift_id + id, 12).zfill(4)

    # def user_id(code: str) -> int:
    #     return from_base(code, 12) - CaatingaConfig._shift_id

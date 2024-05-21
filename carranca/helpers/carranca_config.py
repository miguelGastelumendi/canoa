"""
 Equipe da Canoa -- 2024

 mgd 2024-04-29
"""

from os import path
from .py_helper import to_base, path_remove_last
from main import app_config

class CarrancaConfig:

    _shift_id = 903
    path_html_docs = path.join(app_config.ROOT_FOLDER, 'html_docs')

    # shared scripts with data_validator
    _common = path_remove_last(app_config.ROOT_FOLDER)
    path_uploaded_files = path.join(('.' if _common == None else _common), 'uploaded_files')

    # path to exchange files:
    inter_common = path_remove_last(_common)
    path_data_tunnel = path.join(inter_common, 'data_tunnel')
    folder_validate_output =  'report'

    """ External user code """
    def user_code(id: int) -> str:
        """
            maxInt -> (2**53 - 1) -> 1F FFFF FFFF FFFF -> base 21=> 14f01e5ec7fda
        """
        return to_base(CarrancaConfig._shift_id + id, 21).zfill(5)

    # def user_id(code: str) -> int:
    #     return from_base(code, 12) - CarrancaConfig._shift_id

#eof
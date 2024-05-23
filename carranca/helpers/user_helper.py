# Equipe da Canoa -- 2024
#
# current user helper
#
# mgd

from py_helper import to_base, now

_code_shift_id = 903



def now_as_text():
    # current date time for user
    ##- TODO: get app_config <- from ui_texts
    return now().strftime('%d/%m/%Y às %H:%M')


def user_code(id: int) -> str:
    """
    TODO: generate unique value for user sabe in table
    External user code
    maxInt -> (2**53 - 1) -> 1F FFFF FFFF FFFF -> base 21=> 14f01e5ec7fda
    """
    return to_base(_code_shift_id + id, 21).zfill(5)

# TODO:
# def user_id(code: str) -> int:
#     return from_base(code, 12) - CarrancaConfig._shift_id


#eof
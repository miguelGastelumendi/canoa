# Equipe da Canoa -- 2024
#
# current user helper
#
# mgd

from .py_helper import to_base, now

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


class LoggedUser:
    """
    LoggedUser is a documented option for flask_login' `current_user`

    Args:
        current_user from flask_login

    Attributes:
        - code: Encrypted and unique user code derived from the user ID. (str)
        - id: User's ID. (int)
        - email: User's email address. (str)

    """
    def __init__(self, current_user ):
        self.code = user_code(current_user.id)
        self.id = current_user.id
        self.email = current_user.email

# TODO:
# def user_id(code: str) -> int:
#     return from_base(code, 12) - CarrancaConfig._shift_id


#eof
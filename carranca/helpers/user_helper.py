# Equipe da Canoa -- 2024
#
# current user helper
#
# mgd

from .py_helper import current_milliseconds, to_base, now, crc16

_code_shift_id = 903
_ticket_receipt_sep = '_'

def now_as_text():
    # current date time for user
    ##- TODO: get app_config <- from ui_texts
    return now().strftime('%d/%m/%Y às %H:%M')


def user_code(id: int) -> str:
    """
    generate a unique value for user (based in the user's table PK)
    for external use
    maxInt -> (2**53 - 1) -> 1F FFFF FFFF FFFF -> base 21=> 14f01e5ec7fda
    """
    return to_base(_code_shift_id + id, 21).zfill(5)


def file_ticket(user_code: str) -> str:
    # `user_receipt` (see below) dependes heavily in the format of the file_ticket
    """
    5 : usuário
    _ : separador
    4-2-2: data yyyy-mm-dd
    _ : separador
    6 : ms do dia em base 22
    """
    ms = to_base(current_milliseconds(), 22).zfill(6)  # max = ggi.48g
    now_str = now().strftime('%Y-%m-%d')
    file_ticket = f"{user_code}{_ticket_receipt_sep}{now_str}{_ticket_receipt_sep}{ms}"

    return file_ticket



def user_receipt(ticket: str) -> str:
    parts = ticket.split(_ticket_receipt_sep)
    crc = crc16(_ticket_receipt_sep)
    receipt = f"{parts[1]}{_ticket_receipt_sep}{crc:04X}"

    return receipt


class LoggedUser:
    """
    LoggedUser is a documented option for flask_login' `current_user`

    Params:
        current_user from flask_login

    Args:
        name (str): user's name.
        code (str): Encrypted and unique user code derived from the user ID.
        id (int): User's ID.
        email (str): User's email address.

    """
    def __init__(self, current_user):
        self.name = current_user.username
        self.code = user_code(current_user.id)
        self.id = current_user.id
        self.email = current_user.email


# TODO:
# def user_id(code: str) -> int:
#     return from_base(code, 12) - CarrancaConfig._shift_id




#eof
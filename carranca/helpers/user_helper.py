"""
    Current User information helpers

    mgd
    Equipe da Canoa -- 2024
"""
#cSpell:ignore cuser

from typing import Any
from .py_helper import current_milliseconds, to_base, now, crc16
from flask_login import current_user

_code_shift_id = 903
_ticket_receipt_sep = '_'

def now_as_text() -> str:
    # current date time for user
    ##- TODO: get app_config <- from ui_texts
    return now().strftime('%d/%m/%Y às %H:%M')


def get_user_code(id: int) -> str:
    """
    generate a unique value for user (based in the user's table PK)
    for external use
    maxInt -> (2**53 - 1) -> 1F FFFF FFFF FFFF -> base 21=> 14f01e5ec7fda
    """
    return to_base(_code_shift_id + id, 21).zfill(5)

def get_user_folder(id: int) -> str:
    return get_user_code(id)

def get_file_ticket(user_code: str) -> str:
    """
        1    1  1   1             =  4  separators, _ (underscore) and - (for date)
    4    4    2  2  13            = 25
    0635_2024-04-30_1714523156580 = 29

    4    : usuário
    _    : separador
    4-2-2: data yyyy-mm-dd
    _    : separador
    13    : ms do dia em base 22
    """
    # `user_receipt` (see below) dependes heavily in the format of the file_ticket
    ms = to_base(current_milliseconds(), 22).zfill(6)  # max = ggi.48g
    now_str = now().strftime('%Y-%m-%d')
    file_ticket = f"{user_code}{_ticket_receipt_sep}{now_str}{_ticket_receipt_sep}{ms}"
    return file_ticket


def get_user_receipt(ticket: str) -> str:
    """
    4-2-2: data yyyy-mm-dd
    _    : separador
    3    : crc16 of the `ticket`
    """
    crc = crc16(ticket)
    parts = ticket.split(_ticket_receipt_sep)
    receipt = f"{parts[1]}{_ticket_receipt_sep}{crc:04X}"
    return receipt


class LoggedUser:
    """
    LoggedUser is a documented option for flask_login' `current_user`

    Args:
        name (str): user's name.
        code (str): Encrypted and unique user code derived from the user ID.
        id (int): User's ID.
        email (str): User's email address.

    """
    def __init__(self):
        cuser = current_user
        self.logged = cuser is not None
        if self.logged:
            self.name = cuser.username
            self.code = get_user_code(cuser.id)
            self.folder = get_user_folder(cuser.id)
            self.id = cuser.id
            self.email = cuser.email
        else:
            self.name = ''
            self.code = '0'
            self.folder = ''
            self.id = -1
            self.email = ''


# TODO:
# def user_id(code: str) -> int:
#     return from_base(code, 12) - CarrancaConfig._shift_id


# eof
"""
    *User Roles*
    This is a helper to facilitate
    the selection of users by 'rol'
    (users.id_role) via roles.role


    Equipe da Canoa -- 2024
    mgd
"""

# cSpell:ignore Setorista

from enum import Enum


class Roles(Enum):
    Admin = "ADM"
    Setorista = "SEP"
    Suporte = "SPT"
    Unknown = "UNK"


# eof

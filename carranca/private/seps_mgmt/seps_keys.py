"""
SEP Management and User assignment
Database Column Names & Cargo Keys (data sent from the front-end)

Equipe da Canoa -- 2025
mgd 2025-04-17
"""

# cSpell: ignore mgmt


class MgmtCol:
    # This class defines the columns that are sent to and
    # used in `sp_mgmt``.
    sep_id = "sep_id"  # 0
    icon_url = "icon_url"  # 1
    usr_curr = "user_curr"  # 2
    sep_fn = "sep_fullname"  # 3
    usr_new = "user_new"  # 4
    set_at = "assigned_at"  # 5


class CargoKeys:
    # This class is used to create a the cargo of the response of `sp_mgmt`
    # and parsed sep_mgm_save._prepare_data_to_save
    actions = "actions"
    cargo = "cargo"
    none = "none"


# eof

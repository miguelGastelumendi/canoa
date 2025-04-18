"""
SEP Management and User assignment
Columns names & Cargo keys

Equipe da Canoa -- 2025
mgd 2025-04-17
"""

# cSpell: ignore mgmt


class MgmtCol:
    # This class defines the columns that are sent to and
    # used in `sp_mgmt``.
    sep_id = "sep_id"
    file_url = "file_url"
    sep_fn = "sep_fullname"
    usr_curr = "user_curr"
    usr_new = "user_new"
    set_at = "assigned_at"


class CargoKeys:
    # This class is used to create a the cargo of the response of `sp_mgmt`
    # and parsed sep_mgm_save._prepare_data_to_save
    actions = "actions"
    grid = "grid"
    none = "none"
    remove = "remove"


# eof

"""
Python Types Aliases

Best practice to use `snake_case` (lowercase letters with
underscores) for variable names, including type aliases.

This follows PEP 8 naming conventions.

mgd
Equipe da Canoa -- 2024

cSpell:ignore mgmt
"""

from typing import TypeAlias, Dict, Tuple

ui_db_texts: TypeAlias = Dict[str, str]

sep_mgmt_rtn: TypeAlias = Tuple[str, str, int]


# eof

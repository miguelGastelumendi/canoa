"""
This module defines Python Type Aliases to improve code readability and maintainability.

Type Aliases:
- `ui_db_texts`: Represents a dictionary where both keys and values are strings (read from a DB vw_ui_texts)
- `sep_mgmt_rtn`: Represents a tuple containing two strings and an integer, used if SEP Management
- `cargo_list`: Represents a list of json-like HTML response


*Python Types Aliases*
Best practice to use `snake_case` (lowercase letters with
underscores) for variable names, including type aliases.

This follows PEP 8 naming conventions.

mgd
Equipe da Canoa -- 2024

cSpell:ignore mgmt
"""

from typing import TypeAlias, Dict, Tuple, List, Any

ui_db_texts: TypeAlias = Dict[str, str]

sep_mgmt_rtn: TypeAlias = Tuple[str, str, int]

cargo_item: TypeAlias = Dict[str, str | Dict[str, str]]
cargo_list: TypeAlias = List[cargo_item]

template_file_full_name: TypeAlias = str

# eof

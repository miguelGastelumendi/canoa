"""
This module defines Python Type Aliases to improve code readability and maintainability.

Type Aliases:
- `ui_db_texts`: A dictionary where both keys and values are strings, typically used for database UI texts.
- `sep_mgmt_rtn`: A tuple containing two strings and an integer, used for SEP management return values.
- `cargo_item`: A dictionary representing a JSON-like structure, which may include nested dictionaries.
- `cargo_list`: A list of `cargo_item` dictionaries, representing a JSON-like HTML response.
- `template_file_full_name`: A string representing the full name of a template file.

Naming Conventions:
Type aliases follow `snake_case` naming as per PEP 8 guidelines for better readability and consistency.

Author: Equipe da Canoa, 2024

cSpell:ignore
"""

# --- /!\ ---
# Avoid adding project-specific imports in this module to prevent circular dependencies.

from typing import TypeAlias, Dict, Tuple, List

ui_db_texts: TypeAlias = Dict[str, str]

sep_mgmt_rtn: TypeAlias = Tuple[str, str, int]

cargo_item: TypeAlias = Dict[str, str | Dict[str, str]]
cargo_list: TypeAlias = List[cargo_item]

template_file_full_name: TypeAlias = str
jinja_template: TypeAlias = str

svg_content: TypeAlias = str


# make str type explicit
error_message: TypeAlias = str
success_message: TypeAlias = str
dic_as_json: TypeAlias = str
# eof

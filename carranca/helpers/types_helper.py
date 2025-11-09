"""
This module defines Python Type Aliases to improve code readability and maintainability.

Type Aliases:
- `UiDbTexts`: A dictionary where both keys and values are strings, typically used for database UI texts.
- `SepMgmtReturn`: A tuple containing two strings and an integer, used for SEP management return values.
- `CargoItem`: A dictionary representing a JSON-like structure, which may include nested dictionaries.
- `CargoList`: A list of `CargoItem` dictionaries, representing a JSON-like HTML response.
- `TemplateFileFullName`: A string representing the full name of a template file.

Naming Conventions:
Type aliases follow `snake_case` naming as per PEP 8 guidelines for better readability and consistency.

Author: Equipe da Canoa, 2024

cSpell:ignore
"""

# --- ⚠️ ---
# Avoid adding project-specific imports in this module to prevent circular dependencies.

from typing import TypeAlias, Optional, Any, Dict, Tuple, List

UiDbTexts: TypeAlias = Dict[str, str|bool]
UsualDict: TypeAlias = Dict[str, Any]
JsConstants: TypeAlias = Dict[str, str]

SepMgmtReturn: TypeAlias = Tuple[str|None, str, int]

CargoItem: TypeAlias = Dict[str, str | Dict[str, str]]
CargoList: TypeAlias = List[CargoItem]

TemplateFileFullName: TypeAlias = str
JinjaTemplate: TypeAlias = str
JinjaGeneratedHtml: TypeAlias = str

SvgContent: TypeAlias = str

OptListOfStr: TypeAlias = Optional[List[str]]

OptStr: TypeAlias = Optional[str]

# make str type explicit
ErrorMessage: TypeAlias = str
SuccessMessage: TypeAlias = str
DictAsJson: TypeAlias = str
JsonText: TypeAlias = str
# eof

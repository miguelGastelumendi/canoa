"""

ui-grid <-> py communication constants

mgd

"""

# cSpell:words nsert

import json
from typing import Tuple

from ..helpers.py_helper import to_int

D_SEP = ":"


class GridCargoKeys:
    # Defines the response's cargo keys of `sep_grid` `scm_grid`
    action = "act"
    code = "code"
    index = "idx"
    grid = "grd"
    edit = "E"
    insert = "I"
    delete = "D"


class GridResponse:
    action: str = ""
    code: str = ""
    row_index = 0
    cmd_json: json = None

    def _get_value(key: str) -> str:
        value = GridResponse.cmd_json[key] if key in GridResponse.cmd_json else "?"
        return value

    def __init__(self, cmd_text):
        GridResponse.cmd_json = json.loads(cmd_text)
        GridResponse.action = GridResponse._get_value(GridCargoKeys.action)[0]
        GridResponse.code = GridResponse._get_value(GridCargoKeys.code)
        GridResponse.row_index = GridResponse._get_value(GridCargoKeys.index)

    def do_data() -> str:
        data = GridAction.do_data(GridResponse.action, GridResponse.code, GridResponse.row_index)
        return data


class GridAction:
    # Send command from gris
    add = "!++"
    null = "!~~"
    show = "!##"

    def has_data(data: str) -> bool:
        # action:code
        return D_SEP in data

    def do_data(action: str, code: str, row_index=0) -> str:
        data = f"{action}{D_SEP}{code}{D_SEP}{row_index}"
        return data

    def get_data(data: str) -> Tuple[str, str, str]:
        if not GridAction.has_data(data):
            code = data
            return None, code, None

        """
        action:code:row_index
        -----------
        `action` can be:
            » None: is a call from the menu, no action.
              After edit or insert, return to standard login()
                or
            » [C]reate, [I]nsert, [E]dit
            It is the first char of the button that trigger the action in
                `private/sep_grid.html.j2`
            and routed here via
                `private/rout("/sep_grid/<code>")`
            See sep_grid.html.j2  { -- Action Triggers -- }
            After edit or insert, return to the calling grid & select this row
        """
        action = data.split(D_SEP)[0]

        """
        `code` can be:
            » GridAction.add : insert a new SEP
              or
            » The obfuscate ID of the SEP to edit
        """
        code = data.split(D_SEP)[1]

        """
        `row_index` is the selected row index, selected again on return
        # TODO, now optional
        """
        row_index = to_int(f"{data}{D_SEP}".split(D_SEP)[2], 0)

        return action, code, row_index


# eof

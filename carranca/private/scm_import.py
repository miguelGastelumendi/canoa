"""
Schema & Seps data import

Reverse the action os scm_export, creating a Dict

mgd 2025.08
"""

import json
from typing import Dict
from ..helpers.py_helper import json_to_dict


def do_scm_import(json_string: str) -> Dict:
    """
    Decodes Base64-encoded strings within a dictionary parsed from a JSON string.
    """
    _dict = json.loads(json_string)

    decoded_dic = json_to_dict(_dict, True)

    # TODO

    return decoded_dic

# eof

"""
Class for obfuscating an id/PK


Equipe da Canoa -- 2025
mgd
"""

from typing import Optional
from ..helpers.py_helper import to_base


class IdToCode:
    # This class attribute can serve as a default or for other static uses if any arise.
    base: int = 9

    def __init__(self, instance_base: Optional[int] = 13):
        """
        Initializes the IdToCode instance with a specific base for encoding/decoding.
        """
        self.base = instance_base

    def decode(self, code: str) -> int:
        """
        Converts an obfuscated code string back to an integer ID, using the instance's base.
        """
        try:
            decoded_id = int(int(code, self.base) / self.base)
        except (ValueError, TypeError):
            decoded_id = -1
        return decoded_id

    def encode(self, id_value: int) -> str:
        """
        Generates an obfuscated code string from an ID, using the instance's base.
        """
        return to_base(self.base * id_value, self.base)  # ;-)


# eof

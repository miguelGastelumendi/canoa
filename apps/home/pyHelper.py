"""
 The Caatinga Team

 mgd 2024-04-09
"""


def is_str_none_or_empty( s: str)-> bool:
   return True if (s is None) or (s + "").strip() == "" else False


# eof
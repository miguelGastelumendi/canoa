# Equipe da Canoa -- 2024
#
# Email Helpers
# mgd

# cSpell:ignore
from typing import NewType
from .py_helper import as_str_strip

# -> "email[, name] ; email2[, name2];..."
# eg -> "mjohn.doe@example.com,John Doe;r2r2@example.com"
RecipientsListStr = NewType("RecipientsListStr", str)

# TODO
# class RecipientsListStr:
#     def __init__(self, value: str):
#         self.value = RecipientsListStr(value)
#     def __str__(self):
#          return str(self.value)
# @staticmethod def is_instance(value): return isinstance(value, str)


class RecipientsDic:
    def __init__(self, to: RecipientsListStr = "", cc: RecipientsListStr = "", bcc: RecipientsListStr = ""):
        self.to = to
        self.cc = cc
        self.bcc = bcc


def user_recipient(mail: str, name: str) -> RecipientsListStr:
    return f"{as_str_strip(mail)},{as_str_strip(name)}"


# eof

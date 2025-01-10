"""
 Equipe da Canoa -- 2024

 Email Helpers

 mgd
 2024-12-23, 2025-01-09


"""

# cSpell:ignore

from .py_helper import as_str_strip, is_str_none_or_empty, strip_and_ignore_empty

# MIME _types
mime_types = {
    ".csv": "text/csv",
    ".htm": "text/html",
    ".html": "text/html",
    ".json": "application/json",
    ".pdf": "application/pdf",
    ".txt": "text/plain",
    ".xls": "Microsoft Excel 2007+",
    ".xlsx": "Microsoft Excel 2007+",
}


class RecipientsListStr:
    """
    email_or_recipients_list_items:
        email:
            email address to be used with second param 'name'
        email_or_recipients_list:
            a list of ; separated of RecipientsListItems

    """

    def __init__(self, email_or_recipients_list_items: str, name: str = None):
        # TODO check if value has, at least, one e@mail.c
        param = ""
        if name is None:
            items = email_or_recipients_list_items
            param = items
        else:
            email = email_or_recipients_list_items
            param = f"{as_str_strip(email)},{as_str_strip(name)}"

        self.as_str = param

    def list(self):
        return [] if is_str_none_or_empty(self.as_str) else strip_and_ignore_empty(self.as_str, ";")

    def parse(self, item: str):
        email, name = (item + ", ").split(",")[:2]
        return as_str_strip(email), as_str_strip(name)

    def __str__(self):
        return str(self.as_str)


class RecipientsDic:
    """
    Recipients to, cc, bcc as RecipientsListStr
    """

    def __init__(
        self, to: RecipientsListStr = None, cc: RecipientsListStr = None, bcc: RecipientsListStr = None
    ):
        def _set(rls: RecipientsListStr):
            return RecipientsListStr("") if rls is None else rls

        self.to = _set(to)
        self.cc = _set(cc)
        self.bcc = _set(bcc)


# eof

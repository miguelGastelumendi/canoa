"""
   texts.py
   Retrieve ui texts item for current language
   (refactored from helper.py)
   mgd
"""

# cSpell:ignore getDictResultset dbquery

# from dbquery import getDictResultset, getValues
import apps.home.dbquery as dbquery
from apps.home.pyHelper import is_str_none_or_empty


# Local vars
user_locale = 'pt-br';   # TODO:  browser || user property
msg_not_found = "Message '{0}' (not registered §: {1})";
sec_Error = 'secError';
sec_Success = 'secSuccess';


def get_select(cols: str, section: str, item: str = None):
    # use SQL lower(item) better than item.lower (use db locale)
    item_filter = "" if item is None else f" and (item_lower = lower('{item}'))"
    query = (
        f"select {cols} from caatinga.vw_ui_texts "
        f"where "
        f"(locale = '{user_locale}') and (section_lower = lower('{section}')){item_filter};"
    )
    return query


# returns a dict<string, string>
def get_section(section: str) -> dict[str, str]:
    query = get_select("item, text", section)
    return dbquery.getDictResultset(query)


# returns text e titulo (a descrição do section)
def get_row(item: str, section: str) -> tuple[str, str]:
    select = get_select("text, title", section, item)
    result = dbquery.getValues(select)
    return ("", "") if result == None else result

# returns a dict<string, string> with the HTML info execpt for
def get_html(section: str) -> dict[str, str]:
    imgList = get_text('images', section);
    # filter if not is_str_none_or_empty(imgList)
    # select item, text from vw_ui_texts v where v.section_lower = 'especificacasetor' and item not in ('image3.png',  'image4.png')

    query = get_select("item, text", section)
    return dbquery.getDictResultset(query)


# returns text or, if not exists, a `warning message`
def get_text(item: str, section: str) -> str:
    text, _ = get_row(item, section)
    if text is None:
        text =  msg_not_found.format(item, section)
    return text


def add_msg(item: str, section: str, texts: dict[str, str] = None) -> str:
    value = get_text(item, section)
    if texts != None:
        texts[section] = value
    return value


def add_msg_error(item: str, texts: dict[str, str] = None) -> str:
    return add_msg(item, sec_Error, texts)


def add_msg_success(item: str, texts: dict[str, str] = None) -> str:
    return add_msg(item, sec_Success, texts)


def get_msg_error(item: str) -> str:
    return add_msg_error(item)


def texts_init():
    text, _ = get_row('messageNotFound', sec_Error)
    mnf =  msg_not_found if is_str_none_or_empty(text) else text
    return mnf


msg_not_found = texts_init();

# eof

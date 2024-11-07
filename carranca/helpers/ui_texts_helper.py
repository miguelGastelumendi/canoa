"""
   Equipe da Canoa -- 2024

   texts_Helper.py
   Retrieve ui texts item for current language
   (refactored from helper.py)
   mgd 2024-04-03

"""

# cSpell:ignore getDictResultset connstr adaptabrasil

from .py_helper import is_str_none_or_empty
from .db_helper import retrieve_data
from .jinja_helper import process_pre_templates

# === local var ===========================================
msg_error = "msgError"
msg_success = "msgSuccess"
user_locale = "pt-br"  # TODO:  browser || user property
msg_not_found = "Message '{0}' (not registered §: {1})"

"""
 See table ui_sections.name
 This two sections are special (id=1 & id=2):
 as they group all msg error and msgs success
"""
sec_Error = "secError"
sec_Success = "secSuccess"


# === local def ===========================================
def __get_query(cols: str, section: str, item: str = None):
    # returns Select query for the current locale, section and, eventually, for only one item
    # use SQL lower(item) better than item.lower (use db locale)
    item_filter = "" if item is None else f" and (item_lower = lower('{item}'))"
    # ** /!\ ******************************************************************
    #  don't use <schema>.table_name. Must set
    #  ALTER ROLE canoa_connstr IN DATABASE adaptabrasil SET search_path=canoa;
    query = (
        f"select {cols} from vw_ui_texts "
        f"where "
        f"(locale = '{user_locale}') and (section_lower = lower('{section}')){item_filter};"
    )
    return query


def _get_result_set(query):
    from .db_helper import retrieve_dict

    dict = retrieve_dict(query)
    # TODO texts = process_pre_templates(_texts)
    return dict


def _get_row(item: str, section: str) -> tuple[str, str]:
    """returns tuple(text, title) for the item/section pair"""
    query = __get_query("text, title", section, item)
    result = retrieve_data(query)
    return ("", "") if result is None else result


def _add_msg(item: str, section: str, name: str, texts: dict[str, str] = None, *args) -> str:
    """Retrieves text and optionally adds it to a dictionary.

    Args:
        item: The item identifier.
        section: The section identifier.
        name: The key for the dictionary entry.
        texts: An optional dictionary to store the retrieved text.
        args: Optional arguments for formatting the retrieved text.

    Returns:
        The formatted text.
    """
    s = get_text(item, section)
    try:
        value = "" if s is None else (s.format(*args) if args else s)
    except:
        value = s

    if texts:
        texts[name] = value

    return value


def _texts_init():
    # initialize 'msg_not_found' str
    text, _ = _get_row("messageNotFound", sec_Error)
    mnf = msg_not_found if is_str_none_or_empty(text) else text
    return mnf


# === public ==============================================


def get_html(section: str) -> dict[str, str]:
    """
    returns a dict[str, str] with the HTML info
     TODO except for.. not ready, still working...
    """
    imgList = get_text("images", section)
    # filter if not is_str_none_or_empty(imgList)
    # select item, text from vw_ui_texts v where v.section_lower = 'html_file' and item not in ('image3.png',  'image4.png')
    query = __get_query("item, text", section)
    return _get_result_set(query)


def get_section(section: str) -> dict[str, str]:
    """
    returns a dict[str, str] of the 'section'
    """
    query = __get_query("item, text", section)
    _texts = _get_result_set(query)
    # texts = process_pre_templates(_texts) # TODO:
    return _texts


def get_text(item: str, section: str, default: str = None) -> str:
    """
    returns text for the item/section pair. if not found, a `warning message`
    """
    text, _ = _get_row(item, section)
    if not is_str_none_or_empty(text):
        pass
    elif default is None:
        text = msg_not_found.format(item, section)
    else:
        text = ""
    return text


def add_msg_error(item: str, texts: dict[str, str] = None, *args) -> str:
    """
    returns text for the item/'sec_Error' pair and adds pair to texts => texts.add( text, 'msgError')
    """
    return _add_msg(item, sec_Error, msg_error, texts, *args)


def add_msg_success(item: str, texts: dict[str, str] = None, *args) -> str:
    """
    returns `text` for the [item, 'sec_Success'] pair
    (of the vw_ui_texts wonderful view)
    and adds the pair to `texts` => texts.add(text, 'msgSuccess')
    """
    return _add_msg(item, sec_Success, msg_success, texts, *args)


def get_msg_error(item: str) -> str:
    # returns text for the item/'sec_Error' pair, adds the pair to texts => texts.add( text, 'msgError')
    return add_msg_error(item)


# init msg_not_found
msg_not_found = _texts_init()

# eof

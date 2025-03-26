"""
Equipe da Canoa -- 2024

texts_Helper.py
Retrieve ui texts item for current language
(refactored from helper.py)
mgd 2024-04-03

"""

# cSpell:ignore getDictResultset connstr adaptabrasil

from typing import Optional
from flask_login import current_user

from .pw_helper import is_someone_logged
from .py_helper import is_str_none_or_empty

# TODO from .jinja_helper import process_pre_templates
from .hints_helper import UI_Texts

from ..common.app_constants import APP_LANG
from ..common.app_error_assistant import CanoeStumbled, ModuleErrorCode, RaiseIf

# === Global 'constants' form HTML ui ========================
#  For more info, see table ui_items.name
#  from ui_texts is loaded ( init_form_vars() )


class UI_Texts_Key:
    class Msg:
        info = "msgInfo"
        warn = "msgWarn"
        error = "msgError"
        success = "msgSuccess"

    # TODO   exception = "msgException"

    class Page:
        title = "pageTitle"

    class Form:  # & dialog
        title = "formTitle"
        icon = "iconFileUrl"  # url of an png/svg icon dlg_var_icon = iconFileUrl, dlg_var_icon_id
        date_format = "user_date_format"
        # display only message, not inputs/buttons (see .carranca\templates\layouts\form.html.j2)
        msg_only = "msgOnly"
        btn_close = "btnMsgOnly"

    class Error:
        no_db_conn = "NoDBConnection"
        code = "ups_error_code"
        where = "ups_offending_def"
        http_code = "ups_http_code"


# === File class/var = ========================
class MsgNotFound:
    cache: Optional[str] = None
    default = "Message '{0}' (not registered §: {1})"


"""
 See table ui_sections.name
 This two sections are special (id=1 & id=2):
 as they group all msg error and msgs success
"""
DB_SECTION_ERROR = "secError"
DB_SECTION_SUCCESS = "secSuccess"


# === user locale  ========================================
def ui_texts_locale() -> str:
    locale = (current_user.lang if is_someone_logged() else APP_LANG).lower()
    return locale


# === local def ===========================================
def __get_ui_texts_query(cols: str, section: str, item: Optional[str] = None):
    # returns Select query for the current locale, section and, eventually, for only one item
    # use SQL lower(item) better than item.lower (use db locale)
    item_filter = "" if item is None else f" and (item_lower = lower('{item}'))"

    # ** /!\ ******************************************************************
    #  don't use <schema>.table_name. Must set
    #  ALTER ROLE canoa_connstr IN DATABASE adaptabrasil SET search_path=canoa;
    query = (
        f"select {cols} from vw_ui_texts "
        f"where "
        f"(locale = lower('{ui_texts_locale()}')) and (section_lower = lower('{section}')){item_filter};"
    )
    return query


def msg_not_found() -> str:
    if MsgNotFound.cache:
        return MsgNotFound.cache

    mnf = MsgNotFound.default
    try:
        text, _ = _get_row("messageNotFound", DB_SECTION_ERROR)
        MsgNotFound.cache = MsgNotFound.default if is_str_none_or_empty(text) else text
        mnf = MsgNotFound.cache
    except:
        pass

    return mnf


def _get_result_set(query):
    from .db_helper import retrieve_dict

    result = retrieve_dict(query)
    # TODO texts = process_pre_templates(_texts)
    return result


def _get_row(item: str, section: str) -> tuple[str, str]:
    """returns tuple(text, title) for the item/section pair"""
    from .db_helper import retrieve_data

    query = __get_ui_texts_query("text, title", section, item)
    result = retrieve_data(query)
    return ("", "") if result is None else result


def _add_msg(item: str, section: str, name: str, texts=None, *args) -> str:
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

    if texts:  # add to texts
        texts[name] = value

    return value


# === public ==============================================
def format_ui_item(texts: UI_Texts, key: str, *args):
    result = texts[key]
    try:
        result = result.format(*args)
    except:
        # eat this err, user will see it (TODO log if debug)
        pass

    return result


def get_html(section: str) -> UI_Texts:
    """
    returns a UI_Texts with the HTML info
     TODO except for.. not ready, still working...
    """
    # imgList = get_text("images", section)
    # filter if not is_str_none_or_empty(imgList)
    # select item, text from vw_ui_texts v where v.section_lower = 'html_file' and item not in ('image3.png',  'image4.png')
    query = __get_ui_texts_query("item, text", section)
    return _get_result_set(query)


def get_section(section_name: str) -> UI_Texts:
    """
    returns a UI_Texts of the 'section_name' from table
    """
    if is_str_none_or_empty(section_name):
        items: UI_Texts = {}
    else:
        query = __get_ui_texts_query("item, text", section_name)
        items = _get_result_set(query)

        if items:
            items[UI_Texts_Key.Form.msg_only] = False
            items[UI_Texts_Key.Form.date_format] = ui_texts_locale()
        elif items is None and RaiseIf.no_ui_texts:
            raise CanoeStumbled("", ModuleErrorCode.UI_TEXTS.value, True)

        # texts = process_pre_templates(_texts) # TODO:

    return items


def get_text(item: str, section: str, default: str = None) -> str:
    """
    returns text for the item/section pair. if not found, a `warning message`
    """
    text, _ = _get_row(item, section)
    if not is_str_none_or_empty(text):
        pass
    elif default is None:
        text = msg_not_found().format(item, section)
    else:
        text = default
    return text


def add_msg_error(item: str, texts: UI_Texts = {}, *args) -> str:
    """
    returns text for the [item/'sec_Error'] pair
    and adds pair to texts => texts.add( text, 'msgError')
    """
    return _add_msg(item, DB_SECTION_ERROR, UI_Texts_Key.Msg.error, texts, *args)


def add_msg_fatal(item: str, texts: UI_Texts = {}, *args) -> str:
    """
    Same as add_msg_error, but just displays the message (msg_only)
    """
    msg = add_msg_error(item, texts, *args)
    return msg


def add_msg_success(item: str, texts: UI_Texts = None, *args) -> str:
    """
    returns `text` for the [item, 'sec_Success'] pair
    (of the vw_ui_texts wonderful view)
    and adds the pair to `texts` => texts.add(text, 'msgSuccess')

    Finally sets texts[UITxtKey.Form.msg_only] = True, so the form only displays
    the message (no other form inputs)

    """
    msg = _add_msg(item, DB_SECTION_SUCCESS, UI_Texts_Key.Msg.success, texts, *args)
    texts[UI_Texts_Key.Form.msg_only] = True
    return msg


def get_msg_error(item: str) -> str:
    # returns text for the item/'sec_Error' pair, adds the pair to texts => texts.add( text, 'msgError')
    return add_msg_error(item)


# eof

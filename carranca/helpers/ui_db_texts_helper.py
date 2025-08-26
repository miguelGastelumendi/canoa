"""
Equipe da Canoa -- 2024

ui_db_texts_Helper.py
Retrieve UI texts items, for current user language, from tha DB

mgd 2024-04-03

TODO:
    - remove sections `secSuccess` & `secError`, just add the items on is on
      section. They will be loaded always

"""

# cSpell:ignore getDictResultset connstr adaptabrasil mgmt

from typing import TypeAlias, Optional, Tuple
from flask_login import current_user


from .pw_helper import is_someone_logged
from .py_helper import is_str_none_or_empty

# TODO from .jinja_helper import process_pre_templates
from .types_helper import ui_db_texts

from ..common.app_constants import APP_LANG

# === Global 'constants' for HTML ui flask forms =============
from .. import global_ui_texts_cache # it is used, ignore warn

# ==== UI Texts Constants ====================================
class UITextsKeys:

    class Msg:
        info = "msgInfo"
        warn = "msgWarn"
        error = "msgError"
        success = "msgSuccess"
        fatal = "msgFatal"
        # display only message, no form, inputs/buttons (see .carranca/templates/layouts/form.html.j2 & dialog.html.j2)
        display_only_msg = "msgOnly"

    class Page:
        title = "pageTitle"

    class Form:  # & dialog
        title = "formTitle"
        icon_file = "iconFile"  # only the icon's name
        icon_url = "iconFileUrl"  # url of an png/svg icon dlg_var_icon_url = iconFileUrl, dlg-var-icon-id
        date_format = "userDateFormat"
        # This button is only visible when msg_only is True OR is a Dialog/Document (see document.html.j2)
        btn_close = "btnCloseForm"

    class Fatal:
        no_db_conn = "NoDBConnection"
        code = "UpsErrorCode"
        where = "UpsOffendingDef"
        http_code = "UpsHttpCode"

    class Section:
        """See table ui_sections.nameThis two sections are special (id=1 & id=2):
        as they group all msg error and msgs success"""

        error = "secError"
        success = "secSuccess"
        # this is a special key that has the name of the section loaded in ui_db_Texts,
        # see  get_section
        name = "__section_name__"


cache_key: TypeAlias = Tuple[str, str, Optional[str]]


class UITexts_TableSearch:
    global global_ui_texts_cache
    _LAST_UPDATE_KEY = "last_update"
    _CACHE_INTERNAL_INFO_KEY: cache_key = (" ", "mgmt_data", "key")
    ## TODO SAVE is Cache _CACHE_INTERNAL_INFO_KEY
    _cfg_cache_lifetime_min = (
        0  # int(current_app.config.get("APP_UI_DB_TEXTS_CACHE_LIFETIME_MIN", 0))
    )

    def __init__(self, locale: str, section: str, item: Optional[str] = None):
        self.locale = locale
        self._locale = self.locale.lower()
        # avoid a " " section (see CACHE_INTERNAL_INFO_KEY)
        self.section = section.strip().lower()
        self.item = item.lower() if item else None
        self.value_is_str = self.item is not None
        self.value_is_dict = self.item is None

    def exists(self) -> bool:
        return self.as_tuple in global_ui_texts_cache

    def update(self, texts: ui_db_texts | str) -> None:
        if self._cfg_cache_lifetime_min == 0:
            global_ui_texts_cache[self.as_tuple] = texts

    def get_text(self) -> Optional[ui_db_texts | str]:
        if not self.exists():
            return None
        value: dict | str = global_ui_texts_cache[self.as_tuple]
        return value.copy() if self.value_is_dict else value

    def set_info(self, key: str, info: any) -> None:
        cache_info = self.get_info_value()
        cache_info[key] = info
        global_ui_texts_cache[UITexts_TableSearch._CACHE_INTERNAL_INFO_KEY] = cache_info

    def get_info_value(self) -> dict:
        cache_value = global_ui_texts_cache.get(
            UITexts_TableSearch._CACHE_INTERNAL_INFO_KEY, {}
        )
        return cache_value

    @property
    def as_tuple(self) -> cache_key:
        """Returns a tuple of all three 'indexed' attributes.
        If item is None, the entry contains a dict, else a str.
        """
        return (self.section, self._locale, self.item)


# TODO: refactor it into
class MsgNotFound:
    cache: Optional[str] = None
    default = "Message '{0}' (not registered §: {1})"


# === current user's locale  ================================
def ui_texts_locale() -> str:
    locale = current_user.lang if is_someone_logged() else APP_LANG
    return locale


# === SQL Constructor =======================================
def __get_ui_texts_query(cols: str, table_search: UITexts_TableSearch) -> str:
    # returns Select query for locale, section and, eventually, for only one item.
    # Use SQL lower(item) is better than item.lower because uses db locale.
    optional_item_filter = (
        ""
        if table_search.item is None
        else f" and (item_lower = lower('{table_search.item}'))"
    )

    # ** ⚠️ ******************************************************************
    #  don't use <schema>.table_name. Must set
    #  ALTER ROLE canoa_connstr IN DATABASE adaptabrasil SET search_path=canoa;
    query = (
        f"select {cols} from vw_ui_texts "
        f"where "
        f"(locale = lower('{table_search.locale}')) and (section_lower = lower('{table_search.section}')){optional_item_filter} "
        f"order by 1;"  # help debugging
    )
    return query


# === Data Retrievers =======================================
def __get_table_row(table_search: UITexts_TableSearch) -> tuple[str, str]:
    """returns tuple(text, title) for the item/section pair"""
    from .db_helper import retrieve_rows

    query = __get_ui_texts_query("text, title", table_search)
    result = retrieve_rows(query)
    return ("", "") if not result else result


def _get_query_as_dict(query) -> ui_db_texts:
    """returns UI_Texts for the item/section pair"""
    from .db_helper import retrieve_dict

    result = retrieve_dict(query)
    # TODO texts = process_pre_templates(result)
    return result


# === TODO use cache  ========================================
def _msg_not_found() -> str:  ## THIS IS OUTDATED ##
    if MsgNotFound.cache:
        return MsgNotFound.cache

    mnf = MsgNotFound.default
    try:
        text, _ = __get_table_row("messageNotFound", UITextsKeys.Section.error)
        MsgNotFound.cache = MsgNotFound.default if is_str_none_or_empty(text) else text
        mnf = MsgNotFound.cache
    except:
        pass

    return mnf


def _add_msg(
    item: str, section: str, name: str, texts: Optional[ui_db_texts] = None, *args
) -> str:
    """Retrieves text and adds it to a dictionary.

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

    if texts and value:  # add or refresh
        texts[name] = value

    return value


# =========================================================
# === public ==============================================
def format_ui_item(texts: ui_db_texts, key: str, *args):
    result = texts[key]
    try:
        result = result.format(*args)
    except:
        # eat this err, user will see it (TODO log if debug)
        pass

    return result


# Cached Texts retrievers ==================================
def get_section(section_name: str) -> ui_db_texts:
    """
    returns a UI_Texts of the 'section_name' from table vw_ui_texts
    """
    if is_str_none_or_empty(section_name):
        return {}

    table_cache = UITexts_TableSearch(ui_texts_locale(), section_name)

    if table_cache.exists():
        return table_cache.get_text()
    else:  # not in cache, retrieve section
        query = __get_ui_texts_query("item, text", table_cache)
        items = _get_query_as_dict(query) or {}

        # TODO process_pre_templates(items) # TODO: check if needed
        items[UITextsKeys.Section.name] = section_name
        items[UITextsKeys.Form.date_format] = table_cache.locale
        table_cache.update(items)
        return items.copy()  # Ensures caller gets a copy, preventing cache pollution


def get_text(item: str, section: str, default: str = None) -> str:
    """
    returns text for the item/section pair. if not found, a `warning message`
    """
    table_search = UITexts_TableSearch(ui_texts_locale(), section, item)
    if table_search.exists():
        text = table_search.get_text()
        return text

    text, _ = __get_table_row(table_search)

    if not is_str_none_or_empty(text):
        pass
    elif default is None:
        text = _msg_not_found().format(item, section)
    else:
        text = default

    table_search.update(text)

    return text


def get_app_menu() -> ui_db_texts:
    app_dic = get_section("appMenu")
    return app_dic


# Texts retrievers helpers ==================================
def get_form_texts(section_name: str) -> ui_db_texts:
    items = get_section(section_name)
    if items:
        # items = process_pre_templates(items) # TODO:
        # delete leftover messages, now I'm sure why they're stuck.
        for k in [
            UITextsKeys.Msg.success,
            UITextsKeys.Msg.warn,
            UITextsKeys.Msg.error,
            UITextsKeys.Msg.fatal,
            UITextsKeys.Msg.display_only_msg,
        ]:
            if k in items:  # DEBUG
                print(f"Unexpected item en section {section_name}: {k}.")
    return items


def add_msg_warning(item: str, texts: ui_db_texts = {}, *args) -> str:
    """
    returns text for the [item/'sec_Error'] pair
    and adds pair to texts => texts.add( text, 'msgError')
    """
    return _add_msg(
        item, UITextsKeys.Section.error, UITextsKeys.Msg.error, texts, *args
    )


def add_msg_error(item: str, texts: ui_db_texts = {}, *args) -> str:
    """
    returns text for the [item/'sec_Error'] pair
    and adds pair to texts => texts.add( text, 'msgError')
    """
    return _add_msg(
        item, UITextsKeys.Section.error, UITextsKeys.Msg.error, texts, *args
    )


def add_msg_final(item: str, texts: ui_db_texts = {}, *args) -> str:
    """
    TODO: fatal
    Same as add_msg_error, but sets
    texts[UITxtKey.Msg.display_only_msg] = True,
    so the form only displays the message (no other form inputs)
    """
    msg = add_msg_error(item, texts, *args)
    texts[UITextsKeys.Msg.display_only_msg] = True
    return msg


def add_msg_success(item: str, texts: ui_db_texts = None, *args) -> str:
    """
    returns `text` for the [item, 'sec_Success'] pair
    (of the vw_ui_texts wonderful view)
    and adds the pair to `texts` => texts.add(text, 'msgSuccess')

    Finally sets texts[UITxtKey.Msg.display_only_msg] = True, so the form only displays
    the message (no other form inputs)

    """
    msg = _add_msg(
        item, UITextsKeys.Section.success, UITextsKeys.Msg.success, texts, *args
    )
    texts[UITextsKeys.Msg.display_only_msg] = True
    return msg


def get_msg_error(item: str) -> str:
    # returns text for the item/'sec_Error' pair
    return add_msg_error(item)


# eof

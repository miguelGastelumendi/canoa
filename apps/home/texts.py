"""
   texts.py
   Retrieve texts tag or texto from vw_textos
   (refactored from helper.py)
   mgd
"""

# cSpell:ignore getDictResultset dbquery

# from dbquery import getDictResultset, getValues
import apps.home.dbquery as dbquery


def get_select(cols: str, grupo: str, tag: str = None):
    tagFilter = "" if tag is None else f" and (search_tag = '{tag.lower()}')"
    query = (
        f"select {cols} from caatinga.vw_textos "
        f"where "
        f"(grupo = '{grupo.lower()}'){tagFilter};"
    )
    return query


# returns a dict<string, string>
def get_texts(grupo: str) -> str:
    query = get_select("tag, texto", grupo)
    return dbquery.getDictResultset(query)


# returns texto e titulo (a descrição do grupo)
def get_row(tag: str, grupo: str) -> tuple[str, str]:
    select = get_select("texto, titulo", grupo, tag)
    result = dbquery.getValues(select)
    return ("", "") if result == None else result


# returns texto or, if not exists, a `warning message`
def get_text(tag: str, grupo: str) -> str:
    text, _ = get_row(tag, grupo)
    if text is None:
        text = f"Mensagem '{tag}' (não registrada, {grupo})."
    return text


def add_msg(tag: str, grupo: str, texts: dict[str, str] = None) -> str:
    value = get_text(tag, grupo)
    if texts != None:
        texts[grupo] = value
    return value


def add_msg_error(tag: str, texts: dict[str, str] = None) -> str:
    return add_msg(tag, "msgError", texts)


def add_msg_success(tag: str, texts: dict[str, str] = None) -> str:
    return add_msg(tag, "msgSuccess", texts)


def get_msg_error(tag: str) -> str:
    return add_msg_error(tag)


# eof

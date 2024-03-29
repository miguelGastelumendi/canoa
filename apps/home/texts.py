"""
   texts.py
   Retrieve texts tag or texto from vw_textos
   (refactored from helper.py)
   mgd
"""
# cSpell:ignore getDictResultset dbquery

#from dbquery import getDictResultset, getValues
import apps.home.dbquery as dbquery

def get_select( cols: str, grupo: str, tag: str = None ):
   query = ( f"select {cols} from caatinga.vw_textos "
              f"where "
              f"(grupo = '{grupo.lower()}')"  +
              '' if tag is None else f" and (search_tag = '{tag.lower()}');"
            )
   return query

# returns a dict<string, string>
def get_texts(grupo: str) -> str:
    return dbquery.getDictResultset(get_select('tag, texto', grupo))

def get_text(tag: str, grupo: str) -> str:
    select= get_select('texto', grupo, tag)
    text= dbquery.getValues(select)
    if text is None:
        text= f"Mensagem '{tag}' (não registrada, {grupo}).";
    return text

def add_msg(tag: str, grupo: str, texts: dict[str, str] = None) -> str:
   value = get_text(tag, grupo)
   if (texts != None ):
      texts[grupo] = value
   return value

def add_msg_error(tag: str, texts: dict[str, str] = None) -> str:
   return add_msg(tag, 'msgError', texts)

def add_msg_success(tag: str, texts: dict[str, str] = None) -> str:
   return add_msg(tag, 'msgSuccess', texts)

#eof

import re
import apps.home.dbquery as dbquery
#mgd from flask import escape
from markupsafe import escape
from sqlalchemy import engine
from  apps.home.texts import add_msg


def getValueFromHTMLName(template: str):
    value = re.findall(r'\(.*?\)', template)[0].replace('(', '').replace(')', '')
    template = template[0:template.find('(')] + '.html'
    segment = get_segment(template)
    return value, template, segment

def filterReturns(toFilter):
#    return toFilter
#    br = Markup('<br />')
    br = ''
    if isinstance(toFilter, dict):
        for key, value in toFilter.items():
            toFilter[key] = str(escape(value)).replace('\r\n', br).replace('\r', br).replace('\n', br)
        return toFilter
    elif isinstance(toFilter, str):
        return str(escape(toFilter)).replace('\r\n', br).replace('\r', br).replace('\n', br)

# Helper - Extract current page name from request
def get_segment(request):

    try:
        segment = request.path.split('/')[-1]
        if segment == '':
            segment = 'index'
        return segment
    except:
        return None

def getFormText(form: str):
    return filterReturns(dbquery.getDictResultset(f"select Tag, Texto from suporteusuarioelemento a "
                                    f"inner join suporteusuariogrupo b "
                                    f"on a.idsuporteusuariogrupo = b.id where b.nome = '{form}' or b.nome = 'wizard'"))
# mgd
# def getTexts(group: str):
#     return dbquery.getDictResultset(f"select tag, texto from suporteusuarioelemento a "
#                              f"inner join suporteusuariogrupo b "
#                              f"on a.idsuporteusuariogrupo = b.id where b.nome = '{group.lower()}'")


# def getErrorMessage(tag: str) -> str:
#    return add _ msg(tag)


def getTipText(form: str):
    return dbquery.getJSONStrResultset(
        f"select Texto as text, 'Dica' as title from SuporteUsuarioElemento a "
        f"inner join SuporteUsuarioGrupo b on a.idSuporteUsuarioGrupo = b.id "
        f"where b.Nome = '{form}' and Tag = 'tip'").replace('\r','').replace('\n','')



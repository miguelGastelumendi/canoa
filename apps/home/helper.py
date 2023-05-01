import re
import apps.home.dbquery as  dbquery
from flask import escape
from sqlalchemy import engine


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
    return filterReturns(dbquery.getDictResultset(f"select Tag, Texto from SuporteUsuarioElemento a "
                                    f"inner join SuporteUsuarioGrupo b "
                                    f"on a.idSuporteUsuarioGrupo = b.id where b.Nome = '{form}' or b.Nome = 'wizard'"))

def getTipText(form: str):
    return dbquery.getJSONStrResultset(
        f"select Texto as text, 'Dica' as title from SuporteUsuarioElemento a inner join SuporteUsuarioGrupo b on a.idSuporteUsuarioGrupo = b.id "
        f"where b.Nome = '{form}' and Tag = 'tip'").replace('\r','').replace('\n','')

def getErrorMessage(tag: str):
    return filterReturns(dbquery.getValues(
        f"select Texto from SuporteUsuarioElemento a inner join SuporteUsuarioGrupo b on a.idSuporteUsuarioGrupo = b.id "
        f"where b.Nome = 'errorMessage' and Tag = '{tag}'")[0])

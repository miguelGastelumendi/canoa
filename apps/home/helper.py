import re
import apps.home.dbquery as  dbquery

def getValueFromHTMLName(template: str):
    value = re.findall(r'\(.*?\)', template)[0].replace('(', '').replace(')', '')
    template = template[0:template.find('(')] + '.html'
    segment = get_segment(template)
    return value, template, segment

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
    return dbquery.getDictResultset(f"select Tag, Texto from SuporteUsuarioElemento a "
                                    f"inner join SuporteUsuarioGrupo b "
                                    f"on a.idSuporteUsuarioGrupo = b.id where b.Nome = '{form}' or b.Nome = 'wizard'")

def getTipText(form: str):
    return dbquery.getJSONStrResultset(
        f"select Texto as text, 'Dica' as title from SuporteUsuarioElemento a inner join SuporteUsuarioGrupo b on a.idSuporteUsuarioGrupo = b.id "
        f"where b.Nome = '{form}' and Tag = 'tip'")

def getErrorMessage(tag: str):
    return dbquery.getValues(
        f"select Tag, Texto from SuporteUsuarioElemento a inner join SuporteUsuarioGrupo b on a.idSuporteUsuarioGrupo = b.id "
        f"where b.Nome = 'errorMessage' and Tag = '{tag}'")

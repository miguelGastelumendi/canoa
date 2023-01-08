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

def getFormText(nomeTela: str):
    return dbquery.getDictResultset(f"select tag, Texto from appSuporteTela where nomeTela = '{nomeTela}'")

def getHelpText(nomeTela: str):
    return dbquery.getJSONStrResultset(f"select Texto as text, 'Ajuda' as title from appSuporteTela where nomeTela = '{nomeTela}' and tag = 'help'")
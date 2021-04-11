from mako.template import Template
from mako.lookup import TemplateLookup


def render_results(stanzas, title="Title"):
    mylookup = TemplateLookup(directories=["."])
    mytemplate = Template(filename="templates/rhymes.html", lookup=mylookup)
    return(mytemplate.render(title=title, stanzas=stanzas))

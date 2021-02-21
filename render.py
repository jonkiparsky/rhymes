from mako.template import Template
from mako.lookup import TemplateLookup

def render_results(lines):

    mylookup = TemplateLookup(directories=["."])
    mytemplate = Template(filename="templates/rhymes.html", lookup=mylookup)
    return(mytemplate.render(lines=lines))
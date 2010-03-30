import re

from django.template        import Template, Context
from django.template.loader import get_template

def domainToXML(domain):

    template = get_template("libs/domain.xml")
    context = Context({ 
        "domain":       domain
    })

    xml = template.render(context)
    xml = re.sub("(?<=\n) *\n", "", xml)
    return xml

#enddef

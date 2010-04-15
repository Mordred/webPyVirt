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

def newStoragePoolXML(poolName, poolType, targetPath, format = None, hostname = None, sourcePath = None):

    template = get_template("libs/storagePool.xml")
    context = Context({
        "name":         poolName,
        "type":         poolType,
        "target":       {
            "path":         targetPath,
        },
        "source":       {
            "path":         sourcePath,
            "format":       format,
            "host":         hostname
        }
    })

    xml = template.render(context)
    xml = re.sub("(?<=\n) *\n", "", xml)

    return xml

#enddef

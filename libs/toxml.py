import re

from django.template        import Template, Context
from django.template.loader import get_template

def domainToXML(domain):

    template = get_template("libs/domain.xml")
    context = Context({ 
        "domain":       domain,
        "disks":        domain.disk_set.all(),
        "hostdevices":  domain.hostdevice_set.all(),
        "interfaces":   domain.interface_set.all(),
        "inputdevices": domain.inputdevice_set.all(),
        "graphics":     domain.graphics_set.all(),
        "videos":       domain.video_set.all(),
        "ports":        domain.port_set.all(),
        "sounds":       domain.sound_set.all(),
        "watchdogs":    domain.watchdog_set.all()
    })

    xml = template.render(context)
    xml = re.sub("(?<=\n) *\n", "", xml)
    return xml

#enddef

def newDomainXML(domain, disk, interface, inputDevice):

    template = get_template("libs/domain.xml")
    context = Context({ 
        "domain":       domain,
        "disks":        [ disk ],
        "hostdevices":  [],
        "interfaces":   [ interface ],
        "inputdevices": [ inputDevice ],
        "graphics":     [],
        "videos":       [],
        "ports":        [],
        "sounds":       [],
        "watchdogs":    []
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

def newStorageVolumeXML(name, capacity, format):

    template = get_template("libs/storageVolume.xml")
    context = Context({
        "name":         name,
        "capacity":     capacity,
        "target":       {
            "format":       format,
        }
    })

    xml = template.render(context)
    xml = re.sub("(?<=\n) *\n", "", xml)

    return xml

#enddef

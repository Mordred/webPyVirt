# -*- coding: UTF-8 -*-

import sha, time ,datetime

from django.core.urlresolvers       import reverse
from django.http                    import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts               import render_to_response, get_object_or_404
from django.template                import RequestContext
from django.utils                   import simplejson
from django.utils.translation       import ugettext as _

from webPyVirt.decorators       import secure
from webPyVirt.libs             import virtualization, toxml

from webPyVirt.domains.models       import Domain
from webPyVirt.domains.permissions  import isAllowedTo

from webPyVirt.nodes.permissions    import isAllowedTo as nodeIsAllowedTo
from webPyVirt.nodes.models         import Node

def wizard(request):
    if request.method != "POST" or "secret" not in request.POST or "action" not in request.POST:
        return HttpResponseRedirect("%s" % (reverse("403")))
    #endif

    secret = request.POST['secret']
    action = request.POST['action']

    permis = request.session.get("domains.domain.add", {})
    if secret not in permis:
        return HttpResponseRedirect("%s" % (reverse("403")))
    #endif

    domainData = permis[secret][1]
    domain = domainData['domain']
    node = domain.node

    if not nodeIsAllowedTo(request, node, "add_domain"):
        return HttpResponseRedirect("%s" % (reverse("403")))
    #endif

    data = {
        "status":           200,
        "statusMessage":    _("OK")
    }

    if action == "nodeCheck":
        try:
            virNode = virtualization.virNode(node)
            result = virNode.getInfo()
        except virtualization.ErrorException, e:
            data['nodeStatus'] = False
            data['error'] = unicode(e)
        else:
            data['nodeStatus'] = True
            data['info'] = result
            try:
                freeMemory = virNode.getFreeMemory()
            except virtualization.ErrorException, e:
                data['info']['freeMemory'] = -1
            else:
                data['info']['freeMemory'] = freeMemory
            #endtry
        #endtry
        data['name'] = node.name
        data['uri'] = node.getURI()
    elif action == "loadMetadata":
        data['name'] = domain.name
        data['uuid'] = domain.uuid
        data['description'] = domain.description
    elif action == "saveMetadata":
        domain.name = request.POST['name']
        domain.uuid = request.POST['uuid']
        domain.description = request.POST['description']
    elif action == "loadMemory":
        data['memory'] = domain.memory
        data['vcpu'] = domain.vcpu
    elif action == "saveMemory":
        domain.memory = request.POST['memory']
        domain.vcpu = request.POST['vcpu']
    elif action == "loadVolumes":
        pool = domainData['pool']
        try:
            virNode = virtualization.virNode(node)
            poolInfo = virNode.getStoragePoolInfo(pool)
            result = virNode.listStorageVolumes(pool)
            volumes = [ {
                    "value":        volume,
                    "label":        "%s (%.2f GB)" % \
                        (volume, (float(virNode.getStorageVolumeInfo(pool, volume)['capacity']) / (1024 * 1024 * 1024)))
                } for volume in result ]
        except virtualization.ErrorException, e:
            data['error'] = unicode(e)
        else:
            data['poolInfo'] = poolInfo
            data['volumes'] = volumes
        #endtry

        if "volume" in domainData:
            data['volume'] = domainData['volume']
        #endif
    elif action == "saveVolumes":
        domainData['volume'] = request.POST['volume']
        volumeAction = int(request.POST['volumeAction'])
        if volumeAction == 0:
            volSize = float(request.POST['size'])
            format = request.POST['format']
        #endif

        newVolume = toxml.newStorageVolumeXML(domainData['volume'], volSize, format)
        try:
            virNode = virtualization.virNode(node)
            result = virNode.createStorageVolume(domainData['pool'], newVolume)
        except virtualization.ErrorException, e:
            data['created'] = False
            data['error'] = unicode(e)
        else:
            data['created'] = True
        #endtry
    elif action == "loadStoragePools":
        try:
            virNode = virtualization.virNode(node)
            result = virNode.listStoragePools()
            pools = [ {
                "value":    poolName,
                "label":    "%s (free %.2f GB)" % \
                    (poolName, (float(virNode.getStoragePoolInfo(poolName)['available']) / (1024 * 1024 * 1024)))
                } for poolName in result ]
        except virtualization.ErrorException, e:
            data['nodeStatus'] = False
            data['error'] = unicode(e)
        else:
            data['storagePools'] = pools
        #endtry

        if "pool" in domainData:
            data['pool'] = domainData['pool']
        #endif
    elif action == "saveStoragePools":
        domainData['pool'] = request.POST['pool']
        if "type" in request.POST:
            domainData['poolType'] = request.POST['type']
        #endif
    elif action == "saveNewStoragePool":
        poolName = domainData['pool']
        poolType = domainData['poolType']
        targetPath = request.POST['targetPath']
        if request.POST['format'] == "":
            format = None
        else:
            format = request.POST['format']
        #endif
        if request.POST['hostname'] == "":
            hostname = None
        else:
            hostname = request.POST['hostname']
        #endif
        if request.POST['sourcePath'] == "":
            sourcePath = None
        else:
            sourcePath = request.POST['sourcePath']
        #endif
        newPool = toxml.newStoragePoolXML(poolName, poolType, targetPath, format, hostname, sourcePath)
        try:
            virNode = virtualization.virNode(node)
            result = virNode.createStoragePool(newPool)
        except virtualization.ErrorException, e:
            data['poolCreated'] = False
            data['error'] = unicode(e)
        else:
            data['poolCreated'] = True
            data['poolInfo'] = result
        #endtry
    else:
        data['status'] = 404
        data['statusMessage'] = _("Action not found!")
    #endif

    domainData['domain'] = domain
    permis[secret] = (time.time(), domainData)
    request.session['domains.domain.add'] = permis

    return HttpResponse(simplejson.dumps(data))
#enddef

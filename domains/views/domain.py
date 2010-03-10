# -*- coding: UTF-8 -*-

from django.core.urlresolvers   import reverse
from django.core.paginator      import Paginator, InvalidPage, EmptyPage
from django.db                  import transaction
from django.http                import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts           import render_to_response, get_object_or_404
from django.template            import RequestContext
from django.utils               import simplejson
from django.utils.translation   import ugettext as _

from webPyVirt.decorators       import secure

@secure
def add(request):
    return render_to_response(
        "domains/domain/add.html",
        {
        },
        context_instance=RequestContext(request)
    )
#enddef

@secure
@transaction.commit_on_success
def autoimport(request):
    toImport = request.session.get("nodes.node.autoimport.toImport", None)

    uuid = request.POST.get('uuid')
    if not toImport or not uuid in toImport or request.method == "GET":
        data = {
            "status":           404,
            "statusMessage":    _("OK"),
            "uuid":             uuid
        }
        return HttpResponse(simplejson.dumps(data))
    #endif

    domain, devices = toImport.pop(uuid)

    domain.save()
    for devType, devs in devices.items():
        for device in devs:
            device.domain = domain
            device.save()
        #endfor
    #endfor

    data = {
        "status":           200,
        "statusMessage":    _("OK"),
        "uuid":             domain.uuid
    }

    request.session['nodes.node.autoimport.toImport'] = toImport

    return HttpResponse(simplejson.dumps(data))
#enddef

# -*- coding: UTF-8 -*-
from django.utils.translation   import ugettext as _
from django.http                import HttpResponseForbidden
from django.shortcuts           import render_to_response
from django.template            import RequestContext, loader

from webPyVirt.decorators       import secure

@secure
def home(request):
    return render_to_response("home.html", context_instance=RequestContext(request))
#enddef

@secure
def forbidden(request):
    return HttpResponseForbidden(
        loader.render_to_string("403.html", context_instance=RequestContext(request))
    )
#enddef

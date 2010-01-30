# -*- coding: UTF-8 -*-
from django.utils.translation import ugettext as _
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from webPyVirt.decorators import secure

@secure
def home(request):
    return render_to_response("home.html", context_instance=RequestContext(request))
#enddef

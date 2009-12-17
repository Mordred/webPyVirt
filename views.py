# -*- coding: UTF-8 -*-
from django.utils.translation import ugettext as _
from django.http import HttpResponse

from decorators import secure

@secure
def home(request):
    return HttpResponse("")
#enddef

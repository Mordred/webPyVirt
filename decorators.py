# -*- coding: UTF-8 -*-
from django.http                import HttpResponseRedirect
from django.core.urlresolvers   import reverse
#from django.utils.http          import urlquote

# USAGE @secure
class secure(object):

    def __init__(self, function):
        self.fnc = function
    #enddef

    def __call__(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
#            path = urlquote(request.get_full_path())
            return HttpResponseRedirect("%s" % (reverse("login")))
        #endif

        return self.fnc(request, *args, **kwargs)
    #enddef

#endclass

# -*- coding: UTF-8 -*-
from django.http                import HttpResponseRedirect
from django.core.urlresolvers   import reverse

# USAGE @secure
class secure(object):

    def __init__(self, function):
        self.fnc = function
    #enddef

    def __call__(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect("%s" % (reverse("login")))
        #endif

        return self.fnc(request, *args, **kwargs)
    #enddef

#endclass

# USAGE @permissions( permission )
#       @permissions( [ pemission1, permission2, ... ] )
class permissions(object):

    def __init__(self, permissions, needAll = False):
        self.permissions = None
        self.needAll = needAll

        if type(permissions) is list:
            self.permissions = permissions
        elif type(permissions) in [str, unicode]:
            self.permissions = [ permissions ]
        else:
            raise ValueError("Only list or string is allowed")
        #endif
    #enddef

    def __call__(self, function):
        def checked(request, *args, **kwargs):
            if self.needAll and not request.user.has_perms(permissions):
                return HttpResponseRedirect("%s" % (reverse("403")))
            elif not self.needAll:
                for perm in self.permissions:
                    if request.user.has_perm(perm):
                        return function(request, *args, **kwargs)
                    #endif
                else:
                    return HttpResponseRedirect("%s" % (reverse("403")))
                #endfor
            #endif

            return function(request, *args, **kwargs)
        #enddef

        return checked
    #enddef
#endclass

# -*- coding: UTF-8 -*-

from django.shortcuts               import render_to_response, get_object_or_404

from webPyVirt.domains.models       import Domain, UserDomainAcl
from webPyVirt.domains.misc         import getDomains

def canChangeAcls(request, *args, **kwargs):
    return bool(getDomains(request, "change_acl").count() != 0)
#enddef

def canEditDomains(request, *args, **kwargs):
    return bool(getDomains(request, "change_domain").count() != 0)
#enddef

def canViewDomains(request, *args, **kwargs):
    return bool(getDomains(request, "view_domain").count() != 0)
#enddef

def canRemoveDomains(request, *args, **kwargs):
    return bool(getDomains(request, "delete_domain").count() != 0)
#enddef

def canMigrateDomains(request, *args, **kwargs):
    return bool(getDomains(request, "migrate_domain").count() != 0)
#enddef

def isAllowedTo(request, domain, acl):
    if not domain: return False

    # Superuser
    if request.user.is_superuser: return True

    # Owner
    if domain.owner == request.user: return True

    allowed = None

    # Test USER permissions
    try:
        userDomainAcl = domain.userdomainacl_set.get(user=request.user)
    except UserDomainAcl.DoesNotExist:
        pass # Skip UserDomainAcl
    else:
        if hasattr(userDomainAcl, acl):
            if getattr(userDomainAcl, acl) == False: return False
            allowed = getattr(userDomainAcl, acl)
        else:
            return False
        #endif
    #endtry

    # Test USER GROUP permissions
    groupDomainAcls = domain.groupdomainacl_set.filter(group__in=request.user.groups.all())
    for groupAcl in groupDomainAcls:
        if hasattr(groupAcl, acl):
            if getattr(groupAcl, acl) == False: return False
            elif getattr(groupAcl, acl) == True: allowed = True
        else:
            return False
        #endif
    #endfor

    if allowed == None:
        return False
    else:
        return True
    #endif
#enddef

def canChangeDomainAcl(request, domainId = None, *args, **kwargs):
    if domainId == None: return False

    try:
        domain = Domain.objects.get(id=domainId)
    except Domain.DoesNotExist:
        return False
    #endtry

    return isAllowedTo(request, domain, "change_acl")
#enddef

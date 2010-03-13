# -*- coding: UTF-8 -*-

from django.db.models           import Q

from webPyVirt.domains.models   import Domain

def getDomains(request, domainFilter, search = None):

    if domainFilter == "view_domain":
        userDomainAclQ = Q(userdomainacl__view_domain=True)
        groupDomainAclQ = Q(groupdomainacl__view_domain=True)
        exUserDomainAclQ = Q(userdomainacl__view_domain=False)
        exGroupDomainAclQ = Q(groupdomainacl__view_domain=False)
    elif domainFilter != "owner":
        raise ValueError("Unknown domain filter: `%s`" % (domainFilter))
    #endif

    if request.user.is_superuser:
        domains = Domain.objects.all()
    elif domainFilter == "owner":
        domains = Domain.objects.filter(owner=request.user)
    else:
        groups = request.user.groups.all()

        domains = Domain.objects.filter(
            Q(owner = request.user)
            | (
                (Q(userdomainacl__user=request.user) & userDomainAclQ)
                & ~(Q(groupdomainacl__group__in=groups) & exGroupDomainAclQ)
            )
            | (
                (Q(groupdomainacl__group__in=groups) & groupDomainAclQ)
                & ~(Q(userdomainacl__user=request.user) & exUserDomainAclQ)
            )
        ).distinct()
    #endif

    if search:
       domains = domains.filter(name__icontains=search)
    #endif

    return domains

#enddef

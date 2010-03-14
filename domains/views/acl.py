# -*- coding: UTF-8 -*-

from django.contrib.auth.models     import User, Group
from django.core.urlresolvers       import reverse
from django.http                    import HttpResponseRedirect
from django.shortcuts               import render_to_response, get_object_or_404
from django.template                import RequestContext

from webPyVirt.domains.forms          import DomainAclForm
from webPyVirt.domains.models         import Domain, UserDomainAcl, GroupDomainAcl
from webPyVirt.domains.permissions    import canChangeDomainAcl

from webPyVirt.decorators           import secure, permissions

@secure
def user(request, domainId, userId):
    if not canChangeDomainAcl(request, domainId):
        return HttpResponseRedirect("%s" % (reverse("403")))
    #endif

    managedDomain = get_object_or_404(Domain, id=domainId)
    managedUser = get_object_or_404(User, id=userId)

    if request.method == "POST":
        form = DomainAclForm(request.POST)
        if form.is_valid():
            try:
                userDomainAcl = UserDomainAcl.objects.get(user=managedUser, domain=managedDomain)
                for field, value in form.cleaned_data.items():
                    if hasattr(userDomainAcl, field):
                        setattr(userDomainAcl, field, value)
                    #endif
                #endfor
            except UserDomainAcl.DoesNotExist:
                userDomainAcl = UserDomainAcl(**form.cleaned_data)
                userDomainAcl.domain = managedDomain
                userDomainAcl.user = managedUser
            #endtry

            userDomainAcl.save()

            # Redirect back on manage user page
            return HttpResponseRedirect(
                reverse("domains:acl_user", kwargs={ "userId": userId, "domainId": domainId })
            )
        #endif
    else:
        try:
            userDomainAcl = UserDomainAcl.objects.get(user=managedUser, domain=managedDomain)
        except UserDomainAcl.DoesNotExist:
            form = DomainAclForm()
        else:
            form = DomainAclForm(instance=userDomainAcl)
        #endtry
    #endif

    return render_to_response(
        "domains/acl/user.html",
        {
            "form":             form,
            "managedUser":      managedUser,
            "managedDomain":      managedDomain
        },
        context_instance=RequestContext(request)
    )
#enddef

@secure
def group(request, domainId, groupId):
    if not canChangeDomainAcl(request, domainId):
        return HttpResponseRedirect("%s" % (reverse("403")))
    #endif

    managedGroup = get_object_or_404(Group, id=groupId)
    managedDomain = get_object_or_404(Domain, id=domainId)

    if request.method == "POST":
        form = DomainAclForm(request.POST)
        if form.is_valid():
            try:
                groupDomainAcl = GroupDomainAcl.objects.get(group=managedGroup, domain=managedDomain)
                for field, value in form.cleaned_data.items():
                    if hasattr(groupDomainAcl, field):
                        setattr(groupDomainAcl, field, value)
                    #endif
                #endfor
            except GroupDomainAcl.DoesNotExist:
                groupDomainAcl = GroupDomainAcl(**form.cleaned_data)
                groupDomainAcl.domain = managedDomain
                groupDomainAcl.group = managedGroup
            #endtry

            groupDomainAcl.save()

            # Redirect back on manage user page
            return HttpResponseRedirect(
                reverse("domains:acl_group", kwargs={ "groupId": groupId, "domainId": domainId })
            )
        #endif
    else:
        try:
            groupDomainAcl = GroupDomainAcl.objects.get(group=managedGroup, domain=managedDomain)
        except GroupDomainAcl.DoesNotExist:
            form = DomainAclForm()
        else:
            form = DomainAclForm(instance=groupDomainAcl)
        #endtry
    #endif

    return render_to_response(
        "domains/acl/group.html",
        {
            "form":             form,
            "managedGroup":     managedGroup,
            "managedDomain":      managedDomain
        },
        context_instance=RequestContext(request)
    )
#enddef

# -*- coding: UTF-8 -*-

from django.contrib.auth.models     import User, Group
from django.core.urlresolvers       import reverse
from django.http                    import HttpResponseRedirect
from django.shortcuts               import render_to_response, get_object_or_404
from django.template                import RequestContext

from webPyVirt.nodes.forms          import NodeAclForm
from webPyVirt.nodes.models         import Node, UserNodeAcl, GroupNodeAcl
from webPyVirt.nodes.permissions    import canChangeNodeAcl

from webPyVirt.decorators           import secure, permissions

@secure
def user(request, nodeId, userId):
    if not canChangeNodeAcl(request, nodeId):
        return HttpResponseRedirect("%s" % (reverse("403")))
    #endif

    managedNode = get_object_or_404(Node, id=nodeId)
    managedUser = get_object_or_404(User, id=userId)

    if request.method == "POST":
        form = NodeAclForm(request.POST)
        if form.is_valid():
            try:
                userNodeAcl = UserNodeAcl.objects.get(user=managedUser, node=managedNode)
                for field, value in form.cleaned_data.items():
                    if hasattr(userNodeAcl, field):
                        setattr(userNodeAcl, field, value)
                    #endif
                #endfor
            except UserNodeAcl.DoesNotExist:
                userNodeAcl = UserNodeAcl(**form.cleaned_data)
                userNodeAcl.node = managedNode
                userNodeAcl.user = managedUser
            #endtry

            userNodeAcl.save()

            # Redirect back on manage user page
            return HttpResponseRedirect(
                reverse("nodes:acl_user", kwargs={ "userId": userId, "nodeId": nodeId })
            )
        #endif
    else:
        try:
            userNodeAcl = UserNodeAcl.objects.get(user=managedUser, node=managedNode)
        except UserNodeAcl.DoesNotExist:
            form = NodeAclForm()
        else:
            form = NodeAclForm(instance=userNodeAcl)
        #endtry
    #endif

    return render_to_response(
        "nodes/acl/user.html",
        {
            "form":             form,
            "managedUser":      managedUser,
            "managedNode":      managedNode
        },
        context_instance=RequestContext(request)
    )
#enddef

@secure
def group(request, nodeId, groupId):
    if not canChangeNodeAcl(request, nodeId):
        return HttpResponseRedirect("%s" % (reverse("403")))
    #endif

    managedGroup = get_object_or_404(Group, id=groupId)
    managedNode = get_object_or_404(Node, id=nodeId)

    if request.method == "POST":
        form = NodeAclForm(request.POST)
        if form.is_valid():
            try:
                groupNodeAcl = GroupNodeAcl.objects.get(group=managedGroup, node=managedNode)
                for field, value in form.cleaned_data.items():
                    if hasattr(groupNodeAcl, field):
                        setattr(groupNodeAcl, field, value)
                    #endif
                #endfor
            except GroupNodeAcl.DoesNotExist:
                groupNodeAcl = GroupNodeAcl(**form.cleaned_data)
                groupNodeAcl.node = managedNode
                groupNodeAcl.group = managedGroup
            #endtry

            groupNodeAcl.save()

            # Redirect back on manage user page
            return HttpResponseRedirect(
                reverse("nodes:acl_group", kwargs={ "groupId": groupId, "nodeId": nodeId })
            )
        #endif
    else:
        try:
            groupNodeAcl = GroupNodeAcl.objects.get(group=managedGroup, node=managedNode)
        except GroupNodeAcl.DoesNotExist:
            form = NodeAclForm()
        else:
            form = NodeAclForm(instance=groupNodeAcl)
        #endtry
    #endif

    return render_to_response(
        "nodes/acl/group.html",
        {
            "form":             form,
            "managedGroup":     managedGroup,
            "managedNode":      managedNode
        },
        context_instance=RequestContext(request)
    )
#enddef

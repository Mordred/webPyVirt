# -*- coding: UTF-8 -*-

from django.shortcuts               import render_to_response, get_object_or_404

from webPyVirt.nodes.models         import Node
from webPyVirt.nodes.misc           import getNodes

def canChangeAcls(request, *args, **kwargs):
    # No nodes
    if not Node.objects.count(): return False

    # Test superuser
    if request.user.is_superuser: return True

    # User is owner of some nodes
    if request.user.node_set.count(): return True

    if getNodes(request, "change_acl").count(): return True

    return False
#enddef

def canChangeNodeAcl(request, nodeId = None, *args, **kwargs):
    if nodeId == None: return False

    # Superuser
    if request.user.is_superuser: return True

    try:
        node = Node.objects.get(id=nodeId)
    except Node.DoesNotExist:
        return False
    #endtry

    # Owner
    if node.owner == request.user: return True

    allowed = None

    userNodeAcl = node.usernodeacl_set.get(user=request.user)
    if userNodeAcl.change_acl == False: return False
    allowed = userNodeAcl.change_acl

    groupNodeAcls = node.groupnodeacl_set.filter(group__in=request.user.groups.all())
    for acl in groupNodeAcls:
        if acl.change_acl == False: return False
        elif acl.change_acl == True: allowed = True
    #endfor

    if allowed == None:
        return False
    else:
        return True
    #endif
#enddef

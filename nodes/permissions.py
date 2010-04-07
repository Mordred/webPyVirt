# -*- coding: UTF-8 -*-

from django.shortcuts               import render_to_response, get_object_or_404

from webPyVirt.nodes.models         import Node, UserNodeAcl
from webPyVirt.nodes.misc           import getNodes

def canChangeAcls(request, *args, **kwargs):
    if not getNodes(request, "change_acl").count():
        return False        # No Nodes
    else:
        return True
    #endif
#enddef

def canListNodes(request, *args, **kwargs):
    if not getNodes(request, "view_node").count():
        return False        # No Nodes
    else:
        return True
    #endif
#enddef

def canEditNodes(request, *args, **kwargs):
    if not getNodes(request, "change_node").count():
        return False        # No Nodes
    else:
        return True
    #endif
#enddef

def canRemoveNodes(request, *args, **kwargs):
    if not getNodes(request, "delete_node").count():
        return False        # No Nodes
    else:
        return True
    #endif
#enddef

def canAddDomains(request, *args, **kwargs):
    return bool(getNodes(request, "add_domain").count() != 0)
#enddef

def canAutoimportDomains(request, *args, **kwargs):
    if not getNodes(request, "owner").count():
        return False        # No Nodes
    else:
        return True
    #endif
#enddef

def isAllowedTo(request, node, acl):
    if not node: return False

    # Superuser
    if request.user.is_superuser: return True

    # Owner
    if node.owner == request.user: return True

    allowed = None

    try:
        userNodeAcl = node.usernodeacl_set.get(user=request.user)
    except UserNodeAcl.DoesNotExist:
        pass # Skip UserNodeAcl
    else:
        if hasattr(userNodeAcl, acl):
            if getattr(userNodeAcl, acl) == False: return False
            allowed = getattr(userNodeAcl, acl)
        else:
            return False
        #endif
    #endtry

    groupNodeAcls = node.groupnodeacl_set.filter(group__in=request.user.groups.all())
    for groupAcl in groupNodeAcls:
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

def canChangeNodeAcl(request, nodeId = None, *args, **kwargs):
    if nodeId == None: return False

    try:
        node = Node.objects.get(id=nodeId)
    except Node.DoesNotExist:
        return False
    #endtry

    return isAllowedTo(request, node, "change_acl")
#enddef

def canViewNode(request, nodeId = None, *args, **kwargs):
    if nodeId == None: return False

    try:
        node = Node.objects.get(id=nodeId)
    except Node.DoesNotExist:
        return False
    #endtry

    return isAllowedTo(request, node, "view_node")
#enddef

# -*- coding: UTF-8 -*-

from django.db.models           import Q

from webPyVirt.nodes.models     import Node

def getNodes(request, nodeFilter, search=None, order = "name"):
    if nodeFilter == "change_acl":
        userNodeAclQ = Q(usernodeacl__change_acl=True)
        groupNodeAclQ = Q(groupnodeacl__change_acl=True)
        exUserNodeAclQ = Q(usernodeacl__change_acl=False)
        exGroupNodeAclQ = Q(groupnodeacl__change_acl=False)
    elif nodeFilter == "view_node":
        userNodeAclQ = Q(usernodeacl__view_node=True)
        groupNodeAclQ = Q(groupnodeacl__view_node=True)
        exUserNodeAclQ = Q(usernodeacl__view_node=False)
        exGroupNodeAclQ = Q(groupnodeacl__view_node=False)
    elif nodeFilter == "change_node":
        userNodeAclQ = Q(usernodeacl__change_node=True)
        groupNodeAclQ = Q(groupnodeacl__change_node=True)
        exUserNodeAclQ = Q(usernodeacl__change_node=False)
        exGroupNodeAclQ = Q(groupnodeacl__change_node=False)
    elif nodeFilter == "delete_node":
        userNodeAclQ = Q(usernodeacl__delete_node=True)
        groupNodeAclQ = Q(groupnodeacl__delete_node=True)
        exUserNodeAclQ = Q(usernodeacl__delete_node=False)
        exGroupNodeAclQ = Q(groupnodeacl__delete_node=False)
    elif nodeFilter != "owner":
        raise ValueError("Unknown node filter: `%s`" % (nodeFilter))
    #endif

    if request.user.is_superuser:
        nodes = Node.objects.all()
    elif nodeFilter == "owner":
        nodes = Node.objects.filter(owner=request.user)
    else:
        groups = request.user.groups.all()

        nodes = Node.objects.filter(
            Q(owner = request.user)
            | (
                (Q(usernodeacl__user=request.user) & userNodeAclQ)
                & ~(Q(groupnodeacl__group__in=groups) & exGroupNodeAclQ)
            )
            | (
                (Q(groupnodeacl__group__in=groups) & groupNodeAclQ)
                & ~(Q(usernodeacl__user=request.user) & exUserNodeAclQ)
            )
        ).distinct()
    #endif

    if search:
       nodes = nodes.filter(name__icontains=search)
    #endif

    if order:
        if type(order) is list:
            nodes = nodes.order_by(*order)
        else:
            nodes = nodes.order_by(order)
        #endif
    #endif

    return nodes
#enddef

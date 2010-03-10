# -*- coding: UTF-8 -*-

from django.utils.translation       import ugettext as _
from django.core.urlresolvers       import reverse

from webPyVirt.nodes.permissions    import *

def MENU(request):
    changeAcls = canChangeAcls(request)
    listNodes = canListNodes(request)
    editNodes = canEditNodes(request)
    removeNodes = canRemoveNodes(request)
    autoimportDomains = canAutoimportDomains(request)

    return [
        {   # Section nodes
            "hide":         False,
            "label":        _("Nodes"),
            "items":        [
                {   # List nodes
                    "hide":     not listNodes,
                    "label":    _("List nodes"),
                    "selected": r"node/list/$",
                    "url":      "node_list"
                },
                {   # Add node
                    "hide":     not request.user.has_perm("nodes.add_node"),
                    "label":    _("Add node"),
                    "selected": r"node/add/",
                    "url":      "node_add"
                },
                {   # Edit node
                    "hide":     not editNodes,
                    "label":    _("Edit node"),
                    "selected": r"node/edit/",
                    "url":      "node_edit__select_node"
                },
                {   # Import existed domains
                    "hide":     not autoimportDomains,
                    "label":    _("Autoimport domains"),
                    "selected": r"node/autoimport/",
                    "url":      "node_autoimport__select_node"
                },
                {   # Remove node
                    "hide":     not removeNodes,
                    "label":    _("Remove node"),
                    "selected": r"node/remove/",
                    "url":      "node_remove__select_node"
                },
            ]
        },
        {   # Section permissions
            "hide":         False,
            "label":        _("Permissions"),
            "items":        [
                {   # User ACL
                    "hide":     not changeAcls,
                    "label":    _("User ACL"),
                    "selected": r"acl/user/",
                    "url":      "acl_user__select_node"
                },
                {   # Group ACL
                    "hide":     not changeAcls,
                    "label":    _("Group ACL"),
                    "selected": r"acl/group/",
                    "url":      "acl_group__select_node"
                },
            ]
        }
    ]
#enddef

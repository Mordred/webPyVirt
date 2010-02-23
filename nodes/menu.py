# -*- coding: UTF-8 -*-

from django.utils.translation       import ugettext as _
from django.core.urlresolvers       import reverse

from webPyVirt.nodes.permissions    import *

def MENU(request):
    changeAcls = canChangeAcls(request)

    return [
        {   # Section nodes
            "hide":         False,
            "label":        _("Nodes"),
            "items":        [
                {   # List nodes
                    "hide":     False,
                    "label":    _("List nodes"),
                    "selected": r"$",
                    "url":      "node_list"
                },
                {   # Add node
                    "hide":     not request.user.has_perm("nodes.add_node"),
                    "label":    _("Add node"),
                    "selected": r"node/add/",
                    "url":      "node_add"
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

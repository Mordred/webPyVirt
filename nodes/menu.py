# -*- coding: UTF-8 -*-

from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

def MENU(request):
    return [
        {   # Section nodes
            "hide":         False,
            "label":        _("Nodes"),
            "items":        [
                {   # List nodes
                    "hide":     False,
                    "label":    _("List nodes"),
                    "selected": r"$",
                    "url":      "list_nodes"
                },
                {   # Add node
                    "hide":     False,
                    "label":    _("Add node"),
                    "selected": r"addNode/",
                    "url":      "add_node"
                },
            ]
        },
        {   # Section permissions
            "hide":         False,
            "label":        _("Permissions"),
            "items":        [
                # TODO: Pridat opravnenia
            ]
        }
    ]
#enddef

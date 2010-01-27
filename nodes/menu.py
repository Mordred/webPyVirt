# -*- coding: UTF-8 -*-

from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

MENU = [
    {   # Section nodes
        "hide":         False,
        "label":        _("Nodes"),
        "items":        [
            {   # Add node
                "hide":     False,
                "label":    _("Add node"),
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

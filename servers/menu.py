# -*- coding: UTF-8 -*-

from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

MENU = [
    {   # Section servers
        "hide":         False,
        "label":        _("Servers"),
        "items":        [
            {   # Add server
                "hide":     False,
                "label":    _("Add server"),
                "url":      "add_server"
            },
            {   # Edit user
                "hide":     False,
                "label":    _("Edit server"),
                "url":      "edit_server"
            },
            {   # Edit user
                "hide":     False,
                "label":    _("Remove server"),
                "url":      "delete_server"
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

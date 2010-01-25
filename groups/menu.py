# -*- coding: UTF-8 -*-

from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

MENU = [
    {   # Section edit groups
        "hide":         False,
        "label":        _("Groups"),
        "items":        [
            {   # Add user
                "hide":     False,
                "label":    _("Add group"),
                "url":      "add_group"
            },
            {   # Edit user
                "hide":     False,
                "label":    _("Edit group"),
                "url":      "edit_group"
            },
            {   # Edit user
                "hide":     False,
                "label":    _("Delete group"),
                "url":      "delete_group"
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

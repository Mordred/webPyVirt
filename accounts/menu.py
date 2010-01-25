# -*- coding: UTF-8 -*-

from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

MENU = [
    {   # Section edit user
        "hide":         False,
        "label":        _("Users"),
        "items":        [
            {   # Add user
                "hide":     False,
                "label":    _("Add user"),
                "url":      "add_user"
            },
            {   # Edit user
                "hide":     False,
                "label":    _("Edit user"),
                "url":      "edit_user"
            },
            {   # Edit user
                "hide":     False,
                "label":    _("Delete user"),
                "url":      "delete_user"
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

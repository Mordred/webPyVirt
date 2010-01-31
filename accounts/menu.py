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
                "selected": r"addUser/$",
                "url":      "add_user"
            },
            {   # Manage users
                "hide":     False,
                "label":    _("Manage users"),
                "selected": r"manageUsers/",
                "url":      "manage_users__select_user"
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

# -*- coding: UTF-8 -*-

from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

def MENU(request):
    return [
        {   # Section Users
            "hide":         False,
            "label":        _("Users"),
            "items":        [
                {   # Add user
                    "hide":     not request.user.has_perm("auth.add_user"),
                    "label":    _("Add user"),
                    "selected": r"addUser/$",
                    "url":      "add_user"
                },
                {   # Manage users
                    "hide":     not request.user.has_perm("auth.change_user"),
                    "label":    _("Manage users"),
                    "selected": r"manageUsers/",
                    "url":      "manage_users__select_user"
                },
                {   # Manage users
                    "hide":     not request.user.has_perm("auth.delete_user"),
                    "label":    _("Remove user"),
                    "selected": r"removeUser/",
                    "url":      "remove_user__select_user"
                },
            ]
        },
        {   # Section Groups
            "hide":         False,
            "label":        _("Groups"),
            "items":        [
                {   # Add group
                    "hide":     False,
                    "label":    _("Add group"),
                    "selected": r"addGroup/$",
                    "url":      "add_group"
                },
                {   # Manage groups
                    "hide":     False,
                    "label":    _("Manage groups"),
                    "selected": r"manageGroups/",
                    "url":      "manage_groups__select_group"
                },
                {   # Delete group
                    "hide":     False,
                    "label":    _("Remove group"),
                    "selected": r"removeGroup/",
                    "url":      "remove_group__select_group"
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

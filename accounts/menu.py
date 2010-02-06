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
                    "selected": r"user/add/$",
                    "url":      "user_add"
                },
                {   # Manage users
                    "hide":     not request.user.has_perm("auth.change_user"),
                    "label":    _("Manage users"),
                    "selected": r"user/manage/",
                    "url":      "user_manage__select"
                },
                {   # Manage users
                    "hide":     not request.user.has_perm("auth.delete_user"),
                    "label":    _("Remove user"),
                    "selected": r"user/remove/",
                    "url":      "user_remove__select"
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
                    "selected": r"group/add/$",
                    "url":      "group_add"
                },
                {   # Manage groups
                    "hide":     False,
                    "label":    _("Manage groups"),
                    "selected": r"group/manage/",
                    "url":      "group_manage__select"
                },
                {   # Delete group
                    "hide":     False,
                    "label":    _("Remove group"),
                    "selected": r"group/remove/",
                    "url":      "group_remove__select"
                },
            ]
        },
        {   # Section permissions
            "hide":         False,
            "label":        _("Permissions"),
            "items":        [
#                {   # User permissions
#                    "hide":     False,
#                    "label":    _("User permissions"),
#                    "selected": r"permissions/user/",
#                    "url":      "permissions__select_user"
#                },
            ]
        }
    ]
#enddef

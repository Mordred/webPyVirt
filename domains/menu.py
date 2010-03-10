# -*- coding: UTF-8 -*-

from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

def MENU(request):
    return [
        {   # Section edit user
            "hide":         False,
            "label":        _("Domains"),
            "items":        [
                {   # Add user
                    "hide":     False,
                    "label":    _("Add domain"),
                    "url":      "domain_add"
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

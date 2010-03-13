# -*- coding: UTF-8 -*-

from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

def MENU(request):
    return [
        {   # Section domain
            "hide":         False,
            "label":        _("Domains"),
            "items":        [
                {   # Add domain
                    "hide":     True,
                    "label":    _("Add domain"),
                    "url":      "domain_add"
                },
                {   # Domain detail
                    "hide":     False,
                    "label":    _("Domain detail"),
                    "url":      "domain_detail__select_domain"
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

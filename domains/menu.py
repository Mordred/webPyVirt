# -*- coding: UTF-8 -*-

from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from webPyVirt.domains.permissions  import *

def MENU(request):
    changeAcls = canChangeAcls(request)
    viewDomains = canViewDomains(request)
    removeDomains = canRemoveDomains(request)

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
                    "hide":     not viewDomains,
                    "label":    _("Domain detail"),
                    "url":      "domain_detail__select_domain"
                },
                {   # Remove domain
                    "hide":     not removeDomains,
                    "label":    _("Remove domain"),
                    "url":      "domain_remove__select_domain"
                },
            ]
        },
        {   # Section permissions
            "hide":         False,
            "label":        _("Permissions"),
            "items":        [
                {   # User ACL
                    "hide":     not changeAcls,
                    "label":    _("User ACL"),
                    "selected": r"acl/user/",
                    "url":      "acl_user__select_domain"
                },
                {   # Group ACL
                    "hide":     not changeAcls,
                    "label":    _("Group ACL"),
                    "selected": r"acl/group/",
                    "url":      "acl_group__select_domain"
                },

            ]
        }
    ]
#enddef

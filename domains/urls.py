# -*- coding: UTF-8 -*-
from django.conf.urls.defaults          import *

from webPyVirt.domains.permissions      import *

urlpatterns = patterns("webPyVirt.domains",
    # Domain
    url(
        r"^$",
        "views.domain.index",
        name="domain_index"
    ),
    url(
        r"^domain/add/$",
        "views.domain.add",
        name="domain_add"
    ),
    url(
        r"^domain/autoimport/$",
        "views.domain.autoimport",
        name="domain_autoimport"
    ),
    url(
        r"^domain/detail/$",
        "views.domain.select",
        {
            "next":         "domains:domain_detail",
            "domainFilter": "view_domain",
            "permission":   canViewDomains
        },
        name="domain_detail__select_domain"
    ),
    url(
        r"^domain/detail/(?P<domainId>\d+)/$",
        "views.domain.detail",
        name="domain_detail"
    ),
    url(
        r"^domain/select/autocomplete/(?P<permission>[\dabcdef]+)/$",
        "views.domain.select_autocomplete",
        name="domain_select_autocomplete"
    ),
    url(
        r"^domain/checkStatus/(?P<domainId>\d+)/$",
        "views.domain.checkStatus",
        name="domain_check_status"
    ),

    # ACL
    url(
        r"^acl/user/$",
        "views.domain.select",
        {
            "next":         "domains:acl_user__select_user",
            "domainFilter":   "change_acl",
            "permission":   canChangeAcls
        },
        name="acl_user__select_domain"
    ),
    url(
        r"^acl/user/(?P<domainId>\d+)/(?P<userId>\d+)/$",
        "views.acl.user",
        name="acl_user"
    ),
    url(
        r"^acl/group/$",
        "views.domain.select",
        {
            "next":         "domains:acl_group__select_group",
            "domainFilter":   "change_acl",
            "permission":   canChangeAcls
        },
        name="acl_group__select_domain"
    ),
    url(
        r"^acl/group/(?P<domainId>\d+)/(?P<groupId>\d+)/$",
        "views.acl.group",
        name="acl_group"
    ),

)

urlpatterns += patterns("webPyVirt.accounts",
    url(
        r"^acl/user/(?P<domainId>\d+)/$",
        "views.user.select",
        {
            "next":         "domains:acl_user",
            "permission":   canChangeDomainAcl
        },
        name="acl_user__select_user"
    ),
    url(
        r"^acl/group/(?P<domainId>\d+)/$",
        "views.group.select",
        {
            "next":         "domains:acl_group",
            "permission":   canChangeDomainAcl
        },
        name="acl_group__select_group"
    ),
)

# -*- coding: UTF-8 -*-
from django.conf.urls.defaults          import *

from webPyVirt.domains.permissions      import *

urlpatterns = patterns("webPyVirt.domains",
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
            # TODO: Pridat opravenia
#            "permission":   canEditNodes
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
)

urlpatterns += patterns("",
    url(
        r"^$", 
        "webPyVirt.views.home",
        name="home"
    ),
)

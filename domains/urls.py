# -*- coding: UTF-8 -*-
from django.conf.urls.defaults import *
from django.utils.translation import ugettext as _

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
)

urlpatterns += patterns("",
    url(
        r"^$", 
        "webPyVirt.views.home",
        name="home"
    ),
)

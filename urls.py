# -*- coding: UTF-8 -*-
from django.conf.urls.defaults import *
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.conf import settings

import accounts.urls
import nodes.urls
import domains.urls

urlpatterns = patterns('',
    url(
        r"^$", 
        "webPyVirt.views.home",
        name="home"
    ),
    url(
        r"^login/$", 
        "django.contrib.auth.views.login", 
        { 
            "template_name":    "login.html"
        },
        name="login"
    ),
    url(
        r"^logout/$", 
        "django.contrib.auth.views.logout_then_login",
        {
            "login_url":        "/login/"
        },
        name="logout"
    ),
    url(
        r"^403/$",
        "webPyVirt.views.forbidden",
        name="403"
    ),
    url(
        r"^accounts/",
        include(accounts.urls, namespace="accounts"),
    ),
    url(
        r"^nodes/",
        include(nodes.urls, namespace="nodes")
    ),
    url(
        r"^domains/",
        include(domains.urls, namespace="domains")
    ),
    url(
        r'^jsi18n/$', 
        'django.views.i18n.javascript_catalog',
        { "packages":   ("webPyVirt.conf",), },
        name="jsi18n"
    ),
)

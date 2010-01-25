# -*- coding: UTF-8 -*-
from django.conf.urls.defaults import *
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.conf import settings

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
        r"^accounts/",
        include("webPyVirt.accounts.urls", namespace="accounts"),
    ),
    url(
        r"^groups/",
        include("webPyVirt.groups.urls", namespace="groups")
    ),
    url(
        r"^servers/",
        include("webPyVirt.servers.urls", namespace="servers")
    ),
    url(
        r"^domains/",
        include("webPyVirt.domains.urls", namespace="domains")
    ),
)

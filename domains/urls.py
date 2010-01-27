# -*- coding: UTF-8 -*-
from django.conf.urls.defaults import *
from django.utils.translation import ugettext as _

urlpatterns = patterns('',
    url(
        r"^$", 
        "webPyVirt.views.home",
        name="home"
    ),
    url(
        r"^addUser/$",
        "webPyVirt.views.home",
        name="add_user"
    ),
    url(
        r"^editUser/$",
        "webPyVirt.views.home",
        name="edit_user"
    ),
    url(
        r"^deleteUser/$",
        "webPyVirt.views.home",
        name="delete_user"
    ),
)

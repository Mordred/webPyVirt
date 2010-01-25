# -*- coding: UTF-8 -*-
from django.conf.urls.defaults import *
from django.utils.translation import ugettext as _

urlpatterns = patterns('',
    url(
        r"^$", 
        "views.home",
        name="home"
    ),
    url(
        r"^addUser/$",
        "views.home",
        name="add_group"
    ),
    url(
        r"^editUser/$",
        "views.home",
        name="edit_group"
    ),
    url(
        r"^deleteUser/$",
        "views.home",
        name="delete_group"
    ),
)

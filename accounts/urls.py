# -*- coding: UTF-8 -*-
from django.conf.urls.defaults import *
from django.utils.translation import ugettext as _

urlpatterns = patterns("webPyVirt.accounts",
    url(
        r"^addUser/$",
        "views.addUser",
        name="add_user"
    ),
    url(
        r"^manageUsers/$",
        "views.manageUsers_selectUser",
        name="manage_users__selectUser"
    ),
    url(
        r"^manageUsers/(?P<userId>\d+)/$",
        "views.manageUsers_user",
        name="manage_users__user"
    ),
    url(
        r"^selectUser/autocomplete/$",
        "views.selectUser_autocomplete",
        name="select_user_autocomplete"
    ),
)

#TEMPORARY
urlpatterns += patterns("",
    url(
        r"^$", 
        "webPyVirt.views.home",
        name="home"
    ),
)


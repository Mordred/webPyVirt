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
        "views.selectUser",
        {
            "next":     "accounts:manage_users__user"
        },
        name="manage_users__select_user"
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
    url(
        r"^removeUser/$",
        "views.selectUser",
        {
            "next":     "accounts:remove_user"
        },
        name="remove_user__select_user"
    ),
    url(
        r"^removeUser/(?P<userId>\d+)/$",
        "views.removeUser",
        name="remove_user"
    ),
    url(
        r"^addGroup/$", 
        "views.addGroup",
        name="add_group"
    ),
    url(
        r"^manageGroups/$",
        "views.selectGroup",
        {
            "next":     "accounts:manage_groups__group"
        },
        name="manage_groups__select_group"
    ),
    url(
        r"^manageGroups/(?P<groupId>\d+)/$",
        "views.manageGroups_group",
        name="manage_groups__group"
    ),
    url(
        r"^selectGroup/autocomplete/$",
        "views.selectGroup_autocomplete",
        name="select_group_autocomplete"
    ),
    url(
        r"^removeGroup/$",
        "views.selectGroup",
        {
            "next":     "accounts:remove_group"
        },
        name="remove_group__select_group"
    ),
    url(
        r"^removeGroup/(?P<groupId>\d+)/$",
        "views.removeGroup",
        name="remove_group"
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


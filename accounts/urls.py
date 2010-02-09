# -*- coding: UTF-8 -*-
from django.conf.urls.defaults import *
from django.utils.translation import ugettext as _

urlpatterns = patterns("webPyVirt.accounts",
    # USERS
    url(
        r"^user/add/$",
        "views.user.add",
        name="user_add"
    ),
    url(
        r"^user/manage/$",
        "views.user.select",
        {
            "next":     "accounts:user_manage"
        },
        name="user_manage__select"
    ),
    url(
        r"^user/manage/(?P<userId>\d+)/$",
        "views.user.manage",
        name="user_manage"
    ),
    url(
        r"^user/select/autocomplete/$",
        "views.user.select_autocomplete",
        name="user_select_autocomplete"
    ),
    url(
        r"^user/remove/$",
        "views.user.select",
        {
            "next":     "accounts:user_remove"
        },
        name="user_remove__select"
    ),
    url(
        r"^user/remove/(?P<userId>\d+)/$",
        "views.user.remove",
        name="user_remove"
    ),

    # GROUPS
    url(
        r"^group/add/$", 
        "views.group.add",
        name="group_add"
    ),
    url(
        r"^group/manage/$",
        "views.group.select",
        {
            "next":     "accounts:group_manage"
        },
        name="group_manage__select"
    ),
    url(
        r"^group/manage/(?P<groupId>\d+)/$",
        "views.group.manage",
        name="group_manage"
    ),
    url(
        r"^group/select/autocomplete/$",
        "views.group.select_autocomplete",
        name="group_select_autocomplete"
    ),
    url(
        r"^group/remove/$",
        "views.group.select",
        {
            "next":     "accounts:group_remove"
        },
        name="group_remove__select"
    ),
    url(
        r"^group/remove/(?P<groupId>\d+)/$",
        "views.group.remove",
        name="group_remove"
    ),

    # PERMISSIONS
    url(
        r"^permissions/user/$",
        "views.user.select",
        {
            "next":     "accounts:permissions_user"
        },
        name="permissions_user__select"
    ),
    url(
        r"^permissions/user/(?P<userId>\d+)/$",
        "views.permissions.user",
        name="permissions_user"
    ),
    url(
        r"^permissions/group/$",
        "views.group.select",
        {
            "next":     "accounts:permissions_group"
        },
        name="permissions_group__select"
    ),
    url(
        r"^permissions/group/(?P<groupId>\d+)/$",
        "views.permissions.group",
        name="permissions_group"
    ),
    url(
        r"^permissions/show/$",
        "views.user.select",
        {
            "next":     "accounts:permissions_show"
        },
        name="permissions_show__select"
    ),
    url(
        r"^permissions/show/(?P<userId>\d+)/$",
        "views.permissions.show",
        name="permissions_show"
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


# -*- coding: UTF-8 -*-
from django.conf.urls.defaults      import *

from webPyVirt.nodes.permissions    import *

urlpatterns = patterns("webPyVirt.nodes",
    url(    # TODO
        r"^$", 
        "views.node.index",
        name="node_index"
    ),
    url(
        r"^node/list/$",
        "views.node.list",
        name="node_list"
    ),
    url(
        r"^node/add/$",
        "views.node.add",
        name="node_add"
    ),
    url(
        r"^node/testConnection/$",
        "views.node.testConnection",
        name="node_test_connection"
    ),
    url(
        r"^node/checkStatus/(?P<nodeId>\d+)/$",
        "views.node.checkStatus",
        name="node_check_status"
    ),
    url(
        r"^node/select/autocomplete/(?P<permission>[\dabcdef]+)/$",
        "views.node.select_autocomplete",
        name="node_select_autocomplete"
    ),

    # ACL
    url(
        r"^acl/user/$",
        "views.node.select",
        {
            "next":         "nodes:acl_user__select_user",
            "nodeFilter":   "change_acl",
            "permission":   canChangeAcls
        },
        name="acl_user__select_node"
    ),
    url(
        r"^acl/user/(?P<nodeId>\d+)/(?P<userId>\d+)/$",
        "views.acl.user",
        name="acl_user"
    ),
    url(
        r"^acl/group/$",
        "views.node.select",
        {
            "next":         "nodes:acl_group__select_group",
            "nodeFilter":   "change_acl",
            "permission":   canChangeAcls
        },
        name="acl_group__select_node"
    ),
    url(
        r"^acl/group/(?P<nodeId>\d+)/(?P<groupId>\d+)/$",
        "views.acl.group",
        name="acl_group"
    ),
)

urlpatterns += patterns("webPyVirt.accounts",
    url(
        r"^acl/user/(?P<nodeId>\d+)/$",
        "views.user.select",
        {
            "next":         "nodes:acl_user",
            "permission":   canChangeNodeAcl
        },
        name="acl_user__select_user"
    ),
    url(
        r"^acl/group/(?P<nodeId>\d+)/$",
        "views.group.select",
        {
            "next":         "nodes:acl_group",
            "permission":   canChangeNodeAcl
        },
        name="acl_group__select_group"
    ),

)

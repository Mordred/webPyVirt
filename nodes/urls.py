# -*- coding: UTF-8 -*-
from django.conf.urls.defaults      import *

from webPyVirt.nodes.permissions    import *

urlpatterns = patterns("webPyVirt.nodes",

    # Node
    url(
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
        r"^node/edit/$",
        "views.node.select",
        {
            "next":         "nodes:node_edit",
            "nodeFilter":   "change_node",
            "permission":   canEditNodes
        },
        name="node_edit__select_node"
    ),
    url(
        r"^node/edit/(?P<nodeId>\d+)/$",
        "views.node.edit",
        name="node_edit"
    ),
    url(
        r"^node/autoimport/$",
        "views.node.select",
        {
            "next":         "nodes:node_autoimport",
            "nodeFilter":   "owner",
            "permission":   canAutoimportDomains
        },
        name="node_autoimport__select_node"
    ),
    url(
        r"^node/autoimport/(?P<nodeId>\d+)/$",
        "views.node.autoimport",
        name="node_autoimport"
    ),
    url(
        r"^node/autoimport/list/(?P<secret>[\dabcdef]+)/$",
        "views.node.autoimport_list",
        name="node_autoimport_list"
    ),
    url(
        r"^node/remove/$",
        "views.node.select",
        {
            "next":         "nodes:node_remove",
            "nodeFilter":   "delete_node",
            "permission":   canRemoveNodes
        },
        name="node_remove__select_node"
    ),
    url(
        r"^node/remove/(?P<nodeId>\d+)/$",
        "views.node.remove",
        name="node_remove"
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

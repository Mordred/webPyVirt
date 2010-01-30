# -*- coding: UTF-8 -*-
from django.conf.urls.defaults import *
from django.utils.translation import ugettext as _

urlpatterns = patterns("webPyVirt.nodes",
    url(    # TODO
        r"^$", 
        "views.listNodes",
        name="list_nodes"
    ),
    url(
        r"^addNode/$",
        "views.addNode",
        name="add_node"
    ),
    url(
        r"^testConnection/$", 
        "views.testConnection",
        name="testConnection"
    ),
)

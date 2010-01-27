# -*- coding: UTF-8 -*-
from django.conf.urls.defaults import *
from django.utils.translation import ugettext as _

import views        # Import local view (webPyVirt.nodes.views)

urlpatterns = patterns('',
    url(    # TODO
        r"^$", 
        views.index,
        name="index"
    ),
    url(
        r"^addNode/$",
        views.addNode,
        name="add_node"
    ),
    url(    # TODO
        r"^$", 
        views.index,
        name="add_node_success"
    ),
)

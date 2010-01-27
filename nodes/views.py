# -*- coding: UTF-8 -*-

from django.shortcuts           import render_to_response
from django.template            import RequestContext
from django.http                import HttpResponseRedirect
from django.core.urlresolvers   import reverse

from forms                      import NodeForm

def index(request):
    return render_to_response("nodes/index.html", {}, context_instance=RequestContext(request)) 
#enddef

def addNode(request):
    if request.method == "POST":
        form = NodeForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("nodes:add_node_success"))
        #endif
    else:
        form = NodeForm()
    #endif

    return render_to_response(
        "nodes/addNode_Form.html", 
        {
            "form": form
        }, 
        context_instance=RequestContext(request)
    ) 
#enddef

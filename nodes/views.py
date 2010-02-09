# -*- coding: UTF-8 -*-

from django.shortcuts           import render_to_response
from django.template            import RequestContext
from django.http                import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers   import reverse
from django.utils               import simplejson
from django.utils.translation   import ugettext as _

from forms                      import NodeForm

from webPyVirt.decorators       import secure
from webPyVirt.libs             import virtualization

@secure
def index(request):
    return render_to_response("nodes/index.html", {}, context_instance=RequestContext(request)) 
#enddef

@secure
def listNodes(request):
    return render_to_response("nodes/listNodes.html", {}, context_instance=RequestContext(request)) 
#enddef

@secure
def addNode(request):
    if request.method == "POST":
        form = NodeForm(request.POST)
        if form.is_valid():
            newNode = form.save(commit=False)
            newNode.owner = request.user
            newNode.save()
            return HttpResponseRedirect(reverse("nodes:list_nodes"))
        #endif
    else:
        form = NodeForm()
    #endif

    return render_to_response(
        "nodes/addNode_Form.html", 
        {
            "form":     form
        }, 
        context_instance=RequestContext(request)
    ) 
#enddef

@secure
def testConnection(request):
    if request.method == "POST":
        form = NodeForm(request.POST)
        if form.is_valid():

            testNode = form.save(commit = False)

            result = virtualization.testConnection(testNode)

            data = {
                "status":           200,
                "statusMessage":    "OK",
                "success":          result['success'],
                "error":            "error" in result and result['error'],
                "info":             "info" in result and result['info']
            }
        else:
            data = {
                "status":           400,
                "statusMessage":    "Data not valid!",
                "errors":           [(k, v[0].__unicode__()) for k, v in form.errors.items()]
            }
        #endif

        return HttpResponse(simplejson.dumps(data))
    else:
        return HttpResponseRedirect(reverse("nodes:index"))
    #endif
#enddef

# -*- coding: UTF-8 -*-

import sha, time

from django.core.urlresolvers   import reverse
from django.core.paginator      import Paginator, InvalidPage, EmptyPage
from django.http                import HttpResponseRedirect, HttpResponse
from django.shortcuts           import render_to_response, get_object_or_404
from django.template            import RequestContext
from django.utils               import simplejson
from django.utils.translation   import ugettext as _

from webPyVirt.nodes.forms          import NodeForm, SelectNodeForm
from webPyVirt.nodes.models         import Node, UserNodeAcl, GroupNodeAcl
from webPyVirt.nodes.misc           import getNodes
from webPyVirt.nodes.permissions    import *

from webPyVirt.decorators       import secure, permissions
from webPyVirt.libs             import virtualization
from webPyVirt.menu             import generateMenu

@secure
def index(request):
    leftMenu = generateMenu(request)['left_menu']

    if not len(leftMenu):
        return HttpResponseRedirect("%s" % (reverse("403")))
    #endif

    # Redirect to first available page
    return HttpResponseRedirect(leftMenu[0]['items'][0]['url'])
#enddef

@secure
def list(request):
    nodes = getNodes(request, "view_node")

    if not len(nodes):
        return HttpResponseRedirect("%s" % (reverse("403")))
    #endif

    paginator = Paginator(nodes, 25)

    try:
        page = int(request.GET.get("page", "1"))
    except ValueError:
        page = 1
    #endtry

    try:
        nodes = paginator.page(page)
    except (EmptyPage, InvalidPage):
        nodes = paginator.page(paginator.num_pages)
    #endtry

    return render_to_response(
        "nodes/node/list.html",
        {
            "nodes":        nodes
        },
        context_instance=RequestContext(request)
    )
#enddef

@secure
@permissions("nodes.add_node")
def add(request):
    if request.method == "POST":
        form = NodeForm(request.POST)
        if form.is_valid():
            newNode = form.save(commit=False)
            newNode.owner = request.user
            newNode.save()
            return HttpResponseRedirect(reverse("nodes:node_list"))
        #endif
    else:
        form = NodeForm()
    #endif

    return render_to_response(
        "nodes/node/add.html",
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
        form.fields.pop("name", "")     # We don't need check name
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

@secure
def select(request, next, nodeFilter, permission = None, *args, **kwargs):
    if permission:
        if not permission(request, *args, **kwargs):
            return HttpResponseRedirect("%s" % (reverse("403")))
        #endif
    #endif

    permis = request.session.get("nodes.node.select", {})
    permisHash = sha.sha(request.user.username.upper() + ":" + str(time.time())).hexdigest()
    permis[permisHash] = time.time()

    # Session cleanup
    hashes = permis.keys()
    for per in hashes:
        if (time.time() - permis[per]) > 1800:
            del permis[per]
        #endif
    #endfor

    request.session['nodes.node.select'] = permis

    request.session['nodes.node.select.nodeFilter'] = nodeFilter

    nodes = getNodes(request, nodeFilter)

    paginator = Paginator(nodes, 25)

    try:
        page = int(request.GET.get("page", "1"))
    except ValueError:
        page = 1
    #endtry

    try:
        nodes = paginator.page(page)
    except (EmptyPage, InvalidPage):
        nodes = paginator.page(paginator.num_pages)
    #endtry

    if request.method == "POST":
        form = SelectNodeForm(request.POST)
        if form.is_valid():

            node = get_object_or_404(Node, name=form.cleaned_data['name'])
            if node not in nodes.object_list:
                # User doesn't have permission to view this node
                form._errors['name'] = _("A node with that name does not exist.")
                del form.cleaned_data['name']
            else:
                kwargs['nodeId'] = node.id
                return HttpResponseRedirect(
                    reverse(next, args = args, kwargs = kwargs)
                )
            #endif

        #endif
    else:
        form = SelectNodeForm()
    #endif

    return render_to_response(
        "nodes/node/select.html",
        {
            "nodes":        nodes,
            "form":         form,
            "permission":   permisHash,
            "next":         next,
            "next_args":    args,
            "next_kwargs":  kwargs
        },
        context_instance=RequestContext(request)
    )
#enddef

@secure
def select_autocomplete(request, permission):
    permis = request.session.get("nodes.node.select", {})
    if not permission in permis or (time.time() - permis[permission]) > 1800:
        return HttpResponse(simplejson.dumps([]))
    #endif

    request.session['nodes.node.select'] = permis

    search = request.GET['term']

    nodeFilter = request.session.get('nodes.node.select.nodeFilter', None)

    nodes = getNodes(request, nodeFilter, search)

    data = [ node.name for node in nodes ]

    return HttpResponse(simplejson.dumps(data))
#enddef

@secure
def checkStatus(request, nodeId):
    node = get_object_or_404(Node, id=nodeId)

    if not isAllowedTo(request, node, "view_node"):
        return HttpResponseRedirect("%s" % (reverse("403")))
    #endif

    result = virtualization.testConnection(node)

    data = {
        "status":           200,
        "statusMessage":    "OK",
        "node":             {
            "status":           result['success'],
            "error":            "error" in result and result['error']
        }
    }

    return HttpResponse(simplejson.dumps(data))
#enddef

@secure
def edit(request, nodeId):
    node = get_object_or_404(Node, id=nodeId)

    if not isAllowedTo(request, node, "change_node"):
        return HttpResponseRedirect("%s" % (reverse("403")))
    #endif

    if request.method == "POST":
        form = NodeForm(request.POST, instance=node)
        if form.is_valid():
            node = form.save()

            # Redirect
            return HttpResponseRedirect(
                reverse("nodes:node_edit", kwargs={ "nodeId": node.id })
            )
        #endif
    else:
        form = NodeForm(instance=node)
    #endif

    return render_to_response(
        "nodes/node/edit.html",
        {
            "form":         form,
            "managedNode":  node
        },
        context_instance=RequestContext(request)
    )
#enddef

@secure
def remove(request, nodeId):
    node = get_object_or_404(Node, id=nodeId)

    if not isAllowedTo(request, node, "delete_node"):
        return HttpResponseRedirect("%s" % (reverse("403")))
    #endif

    if request.method == "POST":
        if "yes" in request.POST and node.id == int(request.POST['nodeId']):
            node.delete()
        #endif

        return HttpResponseRedirect(
            reverse("nodes:node_remove__select_node")
        )
    #endif

    return render_to_response(
        "nodes/node/remove.html",
        {
            "managedNode":  node
        },
        context_instance=RequestContext(request)
    )
#enddef

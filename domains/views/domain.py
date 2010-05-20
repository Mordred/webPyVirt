# -*- coding: UTF-8 -*-

import sha, time ,datetime

from django.core.urlresolvers       import reverse
from django.core.paginator          import Paginator, InvalidPage, EmptyPage
from django.db                      import transaction
from django.forms.util              import ErrorList
from django.http                    import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts               import render_to_response, get_object_or_404
from django.template                import RequestContext
from django.utils                   import simplejson
from django.utils.translation       import ugettext as _
from django.views.decorators.cache  import never_cache

from webPyVirt.decorators       import secure
from webPyVirt.libs             import virtualization, toxml
from webPyVirt.menu             import generateMenu

from webPyVirt.domains.misc         import getDomains
from webPyVirt.domains.forms        import SelectDomainForm, AddDomainForm
from webPyVirt.domains.models       import Domain
from webPyVirt.domains.permissions  import isAllowedTo

from webPyVirt.monitor.monitor      import Monitor

from webPyVirt.nodes.permissions    import isAllowedTo as nodeIsAllowedTo
from webPyVirt.nodes.models         import Node

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
def add(request, nodeId):
    node = get_object_or_404(Node, id=nodeId)

    if not nodeIsAllowedTo(request, node, "add_domain"):
        return HttpResponseRedirect("%s" % (reverse("403")))
    #endif

    newDomain = Domain()
    newDomain.node = node
    newDomain.hypervisor_type = node.driver

    permis = request.session.get("domains.domain.add", {})
    permisHash = sha.sha(request.user.username.upper() + ":" + str(time.time())).hexdigest()
    permis[permisHash] = (time.time(), { "domain": newDomain })

    # Session cleanup
    hashes = permis.keys()
    for per in hashes:
        if (time.time() - permis[per][0]) > 3600:
            del permis[per]
        #endif
    #endfor

    request.session['domains.domain.add'] = permis

    return render_to_response(
        "domains/domain/add.html",
        {
            "hash":     permisHash,
            "node":     node
        },
        context_instance=RequestContext(request)
    )
#enddef

@secure
@transaction.commit_on_success
def autoimport(request):
    toImport = request.session.get("nodes.node.autoimport.toImport", None)

    uuid = request.POST.get('uuid')
    if not toImport or not uuid in toImport or request.method == "GET":
        data = {
            "status":           404,
            "statusMessage":    _("OK"),
            "uuid":             uuid
        }
        return HttpResponse(simplejson.dumps(data))
    #endif

    domain, devices = toImport.pop(uuid)

    domain.save()
    for devType, devs in devices.items():
        for device in devs:
            device.domain = domain
            device.save()
        #endfor
    #endfor

    data = {
        "status":           200,
        "statusMessage":    _("OK"),
        "uuid":             domain.uuid
    }

    request.session['nodes.node.autoimport.toImport'] = toImport

    return HttpResponse(simplejson.dumps(data))
#enddef

@secure
def select(request, next, domainFilter, permission = None, *args, **kwargs):
    if permission:
        if not permission(request, *args, **kwargs):
            return HttpResponseRedirect("%s" % (reverse("403")))
        #endif
    #endif

    permis = request.session.get("domains.domain.select", {})
    permisHash = sha.sha(request.user.username.upper() + ":" + str(time.time())).hexdigest()
    permis[permisHash] = time.time()

    # Session cleanup
    hashes = permis.keys()
    for per in hashes:
        if (time.time() - permis[per]) > 1800:
            del permis[per]
        #endif
    #endfor

    request.session['domains.domain.select'] = permis

    request.session['domains.domain.select.domainFilter'] = domainFilter

    domains = getDomains(request, domainFilter)

    if request.method == "POST":
        form = SelectDomainForm(request.POST)
        if form.is_valid():

            domainsAll = Domain.objects.filter(name=form.cleaned_data['name'])

            # Remove these which cannot be selected because of permissions
            allowedDomains = []
            for dom in domainsAll:
                if dom in domains:
                    # Id was sent with name
                    if form.cleaned_data['id'] and dom.id == form.cleaned_data['id']:
                        allowedDomains.append(dom)
                        break
                    #endif

                    # Id wasn't sent with name
                    if not form.cleaned_data['id']:
                        allowedDomains.append(dom)
                    #endif
                #endif
            #endfor

            domains = allowedDomains

            if len(domains) == 1:
                kwargs['domainId'] = domains[0].id
                return HttpResponseRedirect(
                    reverse(next, args = args, kwargs = kwargs)
                )
            elif len(domains) == 0:
                # User doesn't have permission to view domains
                form._errors['name'] = ErrorList([ _("A domain with that name does not exist.") ])
                del form.cleaned_data['name']
            else:   # More than 1 domain
                form._errors['name'] = ErrorList([ _("Please choose which domain you want from list.") ])
                del form.cleaned_data['name']
            #endif

        #endif
    else:
        form = SelectDomainForm()
    #endif

    paginator = Paginator(domains, 25)

    try:
        page = int(request.GET.get("page", "1"))
    except ValueError:
        page = 1
    #endtry

    try:
        domains = paginator.page(page)
    except (EmptyPage, InvalidPage):
        domains = paginator.page(paginator.num_pages)
    #endtry

    return render_to_response(
        "domains/domain/select.html",
        {
            "domains":      domains,
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
    permis = request.session.get("domains.domain.select", {})
    if not permission in permis or (time.time() - permis[permission]) > 1800:
        return HttpResponse(simplejson.dumps([]))
    #endif

    request.session['domains.domain.select'] = permis

    search = request.GET['term']

    domainFilter = request.session.get('domains.domain.select.domainFilter', None)

    domains = getDomains(request, domainFilter, search)

    data = [ {
        "label":    "%s (%s)" % (domain.name, domain.node.name),
        "value":    domain.name,
        "id":       domain.id
    } for domain in domains ]

    return HttpResponse(simplejson.dumps(data))
#enddef

@secure
def detail(request, domainId):
    domain = get_object_or_404(Domain, id=domainId)

    if not isAllowedTo(request, domain, "view_domain"):
        return HttpResponseRedirect("%s" % (reverse("403")))
    #endif

    secrets = request.session.get("domains.domain.command", {})
    secret = sha.sha(str(domain.id) + ":" + str(time.time())).hexdigest()
    secrets[secret] = (domainId, time.time())

    # Session cleanup
    hashes = secrets.keys()
    for per in hashes:
        if (time.time() - secrets[per][1]) > 1800:
            del secrets[per]
        #endif
    #endfor

    request.session['domains.domain.command'] = secrets

    return render_to_response(
        "domains/domain/detail.html",
        {
            "managedDomain":    domain,
            "secret":           secret,
            "run":              isAllowedTo(request, domain, "resume_domain"),
            "shutdown":         isAllowedTo(request, domain, "shutdown_domain"),
            "suspend":          isAllowedTo(request, domain, "suspend_domain"),
            "reboot":           isAllowedTo(request, domain, "reboot_domain"),
            "save":             isAllowedTo(request, domain, "save_domain")
        },
        context_instance=RequestContext(request)
    )
#enddef

@secure
@never_cache
def checkStatus(request, domainId):
    domain = get_object_or_404(Domain, id=domainId)

    if not isAllowedTo(request, domain, "view_domain"):
        return HttpResponseRedirect("%s" % (reverse("403")))
    #endif

    data = {
        "status":           200,
        "statusMessage":    _("OK")
    }

    try:
        virDomain = virtualization.virDomain(domain)
        status = virDomain.getState()
        del virDomain
    except virtualization.ErrorException, e:
        data['status'] = 503
        data['statusMessage'] = _(unicode(e))
        return HttpResponse(simplejson.dumps(data))
    #endtry

    textStatus = [ _("No state"), _("Running"), _("Idle"),
        _("Paused"), _("Shutdown"), _("Shutoff"), _("Crashed") ][status]
    data['domain'] = {
        "textStatus":   textStatus,
        "status":       status
    }

    return HttpResponse(simplejson.dumps(data))
#enddef

@secure
@never_cache
def command(request):
    if not request.method == "POST" or not "command" in request.POST \
        or not "secret" in request.POST:
        raise Http404
    #endif

    secret = request.POST['secret']
    command = request.POST['command']

    if command not in [ "run", "shutdown", "suspend", "reboot", "save", "destroy" ]:
        raise Http404
    #endif

    secrets = request.session.get("domains.domain.command", {})
    if not secret in secrets or (time.time() - secrets[secret][1]) > 1800:
        raise Http404
    #endif

    domainId = secrets[secret][0]

    domain = get_object_or_404(Domain, id=domainId)

    data = {
        "status":           200,
        "statusMessage":    _("OK")
    }

    # Test Permissions
    if (command == "run" and not isAllowedTo(request, domain, "resume_domain")) \
        or (command == "shutdown" and not isAllowedTo(request, domain, "shutdown_domain")) \
        or (command == "suspend" and not isAllowedTo(request, domain, "suspend_domain")) \
        or (command == "reboot" and not isAllowedTo(request, domain, "reboot_domain")) \
        or (command == "save" and not isAllowedTo(request, domain, "save_domain")) \
        or (command == "destroy" and not isAllowedTo(request, domain, "delete_domain")):
        data['status'] = 403
        data['statusMessage'] = _("You don't have permission to do this.")
    #endif

    try:
        virDomain = virtualization.virDomain(domain)
        if command == "run":
            status = virDomain.getState()
            # TODO: If domain is shutoff --> start it (or recreate)
            if status == virtualization.DOMAIN_STATE_PAUSED:
                virDomain.resume()
            elif status == virtualization.DOMAIN_STATE_SHUTOFF:
                virDomain.run()
            #endif
        elif command == "shutdown":
            virDomain.shutdown()
        elif command == "suspend":
            virDomain.suspend()
        elif command == "reboot":
            virDomain.reboot()
        elif command == "save":
            # TODO: Generate some name for the file
            # where the domain will be saved
            # Not Implemented
            data['status'] = 501
            data['status'] = _("Currently unsupported by Libvirt.")
        elif command == "destroy":
            virDomain.destroy()
        #endif
    except virtualization.ErrorException, e:
        data['status'] = 503
        data['statusMessage'] = _(unicode(e))
    #endtry

    return HttpResponse(simplejson.dumps(data))
#enddef

@secure
def statistics(request, statisticsType):
    if request.method == "GET" or not "visualization" in request.POST \
        or not "domainId" in request.POST:
        raise Http404
    #endif

    visualization = request.POST['visualization']
    domainId = int(request.POST['domainId'])

    domain = get_object_or_404(Domain, id=domainId)

    #TODO: Test if user has permission to the domain

    data = {
        "status":           200,
        "statusMessage":    _("OK")
    }

    monitor = Monitor()
    if not monitor.isRunning():
        data['status'] = 503,
        data['statusMessage'] = _("Monitor is not running")
        return HttpResponse(simplejson.dumps(data))
    #endif

    if visualization.lower() == "gauge":
        stats = domain.statistics_set.order_by("-datetime")[0]
        if statisticsType.lower() == "cpu":
            data['data'] = "%.2f" % (stats.percentage_cpu)
        elif statisticsType.lower() == "memory":
            data['data'] =  "%.2f" % (stats.percentage_memory)
        #endif
    elif visualization.lower() == "areachart":
        lastId = int(request.POST['lastId'])

        now = datetime.datetime.now()
        # Select only last 1,5 minute
        stats = domain.statistics_set.filter(datetime__range=(now - datetime.timedelta(minutes=1), now))\
            .filter(id__gt=lastId).order_by("-datetime")[:20]
        if statisticsType.lower() == "cpu":
            data['data'] = [ {
                "time":     time.mktime(stat.datetime.timetuple()),
                "value":    "%.2f" % (stat.percentage_cpu),
                "id":       stat.id
                } for stat in stats ]
        elif statisticsType.lower() == "memory":
            data['data'] = [ {
                "time":     time.mktime(stat.datetime.timetuple()),
                "value":    "%.2f" % (stat.percentage_memory),
                "id":       stat.id
                } for stat in stats ]
        #endif
    else:
        data['status'] == 404
        data['statusMessage'] = _("Unsupported visualization")
    #endif

    return HttpResponse(simplejson.dumps(data))
#enddef

@secure
def remove(request, domainId):
    domain = get_object_or_404(Domain, id=domainId)

    if not isAllowedTo(request, domain, "delete_domain"):
        return HttpResponseRedirect("%s" % (reverse("403")))
    #endif

    secrets = request.session.get("domains.domain.command", {})
    secret = sha.sha(str(domain.id) + ":" + str(time.time())).hexdigest()
    secrets[secret] = (domainId, time.time())

    # Session cleanup
    hashes = secrets.keys()
    for per in hashes:
        if (time.time() - secrets[per][1]) > 1800:
            del secrets[per]
        #endif
    #endfor

    request.session['domains.domain.command'] = secrets

    if request.method == "POST":
        if "yes" in request.POST and domain.id == int(request.POST['domainId']):
            domain.delete()
        #endif

        return HttpResponseRedirect(
            reverse("domains:domain_remove__select_domain")
        )
    #endif

    return render_to_response(
        "domains/domain/remove.html",
        {
            "managedDomain":    domain,
            "secret":           secret
        },
        context_instance=RequestContext(request)
    )
#enddef

@secure
def edit(request, domainId):
    domain = get_object_or_404(Domain, id=domainId)

    if not isAllowedTo(request, domain, "change_domain"):
        return HttpResponseRedirect("%s" % (reverse("403")))
    #endif

    secrets = request.session.get("domains.domain.edit", {})
    secret = sha.sha(str(domain.id) + ":" + str(time.time())).hexdigest()
    secrets[secret] = (domainId, time.time())

    # Session cleanup
    hashes = secrets.keys()
    for per in hashes:
        if (time.time() - secrets[per][1]) > 1800:
            del secrets[per]
        #endif
    #endfor

    request.session['domains.domain.edit'] = secrets

    return render_to_response(
        "domains/domain/edit.html",
        {
            "managedDomain":    domain,
            "secret":           secret
        },
        context_instance=RequestContext(request)
    )
#enddef

@secure
def edit_ajax(request):
    if request.method != "POST" or "secret" not in request.POST:
        raise Http404
    #endif

    secret = request.POST['secret']
    secrets = request.session.get("domains.domain.edit", {})
    if not secret in secrets or (time.time() - secrets[secret][1]) > 1800:
        raise Http404
    #endif

    domainId = secrets[secret][0]

    domain = get_object_or_404(Domain, id=domainId)

    data = {
        "status":           200,
        "statusMessage":    _("OK")
    }

    try:
        virDomain = virtualization.virDomain(domain)
        if "vcpu" in request.POST:
            vcpus = int(request.POST['vcpu'])
            virDomain.setVCPUs(vcpus)
        elif "max_memory" in request.POST:
            memory = int(request.POST['max_memory'])
            virDomain.setMaxMemory(memory)
        elif "cur_memory" in request.POST:
            memory = int(request.POST['cur_memory'])
            virDomain.setMemory(memory)
        else:
            data['status'] = 404
            data['statusMessage'] = _("Parameter not found!")
        #endif
    except virtualization.ErrorException, e:
        data['status'] = 503
        data['statusMessage'] = _(unicode(e))
    #endtry

    return HttpResponse(simplejson.dumps(data))
#enddef

@secure
def migrate(request, domainId):
    domain = get_object_or_404(Domain, id=domainId)

    if not isAllowedTo(request, domain, "migrate_domain"):
        return HttpResponseRedirect("%s" % (reverse("403")))
    #endif

    permis = request.session.get("domains.domain.migrate", {})
    permisHash = sha.sha(request.user.username.upper() + ":" + str(time.time())).hexdigest()
    permis[permisHash] = (time.time(), { "domain": domain })

    # Session cleanup
    hashes = permis.keys()
    for per in hashes:
        if (time.time() - permis[per][0]) > 3600:
            del permis[per]
        #endif
    #endfor

    request.session['domains.domain.migrate'] = permis

    return render_to_response(
        "domains/domain/migrate.html",
        {
            "domain":    domain,
            "secret":    permisHash
        },
        context_instance=RequestContext(request)
    )
#enddef

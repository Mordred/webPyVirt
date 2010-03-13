# -*- coding: UTF-8 -*-

import sha, time

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
from webPyVirt.libs             import virtualization

from webPyVirt.domains.misc     import getDomains
from webPyVirt.domains.forms    import SelectDomainForm
from webPyVirt.domains.models   import Domain

@secure
def add(request):
    return render_to_response(
        "domains/domain/add.html",
        {
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

    # TODO: Send also ID
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

    # TODO: Test permissions "can view"

    return render_to_response(
        "domains/domain/detail.html",
        {
            "managedDomain":    domain,
        },
        context_instance=RequestContext(request)
    )
#enddef

@secure
@never_cache
def checkStatus(request, domainId):
    domain = get_object_or_404(Domain, id=domainId)

    # TODO: Test permissions "can view"

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

    import logging
    logging.debug("Check Status: %s" % (status))

    textStatus = [ _("No state"), _("Running"), _("Blocked"),
        _("Paused"), _("Shutdown"), _("Shutoff"), _("Crashed") ][status]
    data['domain'] = { "status": textStatus }

    return HttpResponse(simplejson.dumps(data))
#enddef

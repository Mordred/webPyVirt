# -*- coding: UTF-8 -*-

import sha, time

from django.shortcuts           import render_to_response, get_object_or_404
from django.contrib.auth.models import Group, User
from django.template            import RequestContext
from django.http                import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers   import reverse
from django.core.paginator      import Paginator, InvalidPage, EmptyPage
from django.utils               import simplejson

from webPyVirt.decorators       import secure, permissions

from webPyVirt.accounts.forms   import AddGroupForm, SelectGroupForm

@secure
@permissions("auth.add_group")
def add(request):
    if request.method == "POST":
        form = AddGroupForm(request.POST)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("accounts:home"))
        #endif
    else:
        form = AddGroupForm()
    #endif

    return render_to_response(
        "accounts/group/add.html", 
        {
            "form":     form
        }, 
        context_instance=RequestContext(request)
    ) 
#enddef

@secure
def select(request, next, permission = None, *args, **kwargs):

    if permission:
        if not permission(request, *args, **kwargs):
            return HttpResponseRedirect("%s" % (reverse("403")))
        #endif
    #endif

    permis = request.session.get("accounts.group.select", {})
    permisHash = sha.sha(request.user.username.upper() + ":" + str(time.time())).hexdigest()
    permis[permisHash] = time.time()

    # Session cleanup
    for per in permis:
        if (time.time() - permis[per]) > 1800:
            del permis[per]
        #endif
    #endfor

    request.session['accounts.group.select'] = permis

    groups = Group.objects.all().order_by("name")
    paginator = Paginator(groups, 25)

    try:
        page = int(request.GET.get("page", "1"))
    except ValueError:
        page = 1
    #endtry

    try:
        groups = paginator.page(page)
    except (EmptyPage, InvalidPage):
        groups = paginator.page(paginator.num_pages)
    #endtry

    if request.method == "POST":
        form = SelectGroupForm(request.POST)
        if form.is_valid():

            group = get_object_or_404(Group, name=form.cleaned_data['name'])

            kwargs["groupId"] = group.id
            return HttpResponseRedirect(
                reverse(next, args=args, kwargs=kwargs)
            )
        #endif
    else:
        form = SelectGroupForm()
    #endif

    return render_to_response(
        "accounts/group/select.html", 
        {
            "groups":       groups,
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
    permis = request.session.get("accounts.group.select", {})
    if not permission in permis or (time.time() - permis[permission]) > 1800:
        return HttpResponse(simplejson.dumps([]))
    #endif

    request.session['accounts.group.select'] = permis

    search = request.GET['term']

    groups = Group.objects.filter(name__icontains = search)

    data = [ group.name for group in groups ]
    
    return HttpResponse(simplejson.dumps(data))
#enddef

@secure
@permissions("auth.change_group")
def manage(request, groupId):
    group = get_object_or_404(Group, id=groupId)
    availableUsers = User.objects.all().order_by("username")

    selected = request.session.get("selected", 0)
    if "selected" in request.session: del request.session['selected']

    if request.method == "POST":
        if "membersForm" in request.POST:

            if "addUser" in request.POST and len(request.POST['addUser']):
                user = get_object_or_404(User, id=int(request.POST['addUser']))
                group.user_set.add(user)
            #endif

            # Remove selected users
            usersToRemove = []
            for user in group.user_set.all():
                if "user_%s" % user.id in request.POST:
                    usersToRemove.append(user)
                #endif
            #endfor
            if len(usersToRemove): group.user_set.remove(*usersToRemove)

            request.session['selected'] = 0             # JS - nastav aktivnu zalozku
        #endif

        return HttpResponseRedirect(
            reverse("accounts:group_manage", kwargs={ "groupId": group.id })
        )

        #endif
    else:
        pass
    #endif

    return render_to_response(
        "accounts/group/manage.html", 
        {
            "managedGroup":     group,
            "availableUsers":   availableUsers,
            "selected":         selected
        }, 
        context_instance=RequestContext(request)
    ) 
#enddef

@secure
@permissions("auth.delete_group")
def remove(request, groupId):
    group = get_object_or_404(Group, id=groupId)

    if request.method == "POST":
        if "yes" in request.POST and group.id == int(request.POST['groupId']):
            group.delete()
        #endif

        return HttpResponseRedirect(
            reverse("accounts:group_remove__select")
        )
    #endif

    return render_to_response(
        "accounts/group/remove.html",
        {
            "managedGroup":     group
        },
        context_instance=RequestContext(request)
    )
#enddef

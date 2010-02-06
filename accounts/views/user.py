# -*- coding: UTF-8 -*-

from django.shortcuts           import render_to_response
from django.contrib.auth.forms  import UserCreationForm
from django.contrib.auth.models import User, Group
from django.template            import RequestContext
from django.http                import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers   import reverse
from django.core.paginator      import Paginator, InvalidPage, EmptyPage
from django.utils               import simplejson

from webPyVirt.decorators       import secure

from webPyVirt.accounts.forms   import SelectUserForm, UserOverviewForm


@secure
def add(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("accounts:home"))
        #endif
    else:
        form = UserCreationForm()
    #endif

    return render_to_response(
        "accounts/user/add.html", 
        {
            "form":     form
        }, 
        context_instance=RequestContext(request)
    ) 
#enddef

@secure
def select(request, next):
    users = User.objects.all().order_by("username")
    paginator = Paginator(users, 25)

    try:
        page = int(request.GET.get("page", "1"))
    except ValueError:
        page = 1
    #endtry

    try:
        users = paginator.page(page)
    except (EmptyPage, InvalidPage):
        users = paginator.page(paginator.num_pages)
    #endtry

    if request.method == "POST":
        form = SelectUserForm(request.POST)
        if form.is_valid():

            user = User.objects.get(username=form.cleaned_data['username'])

            return HttpResponseRedirect(
                reverse(next, kwargs={ "userId": user.id })
            )
        #endif
    else:
        form = SelectUserForm()
    #endif

    return render_to_response(
        "accounts/user/select.html", 
        {
            "users":    users,
            "form":     form,
            "next":     next
        }, 
        context_instance=RequestContext(request)
    ) 
#enddef

@secure
def select_autocomplete(request):
    search = request.GET['term']

    users = User.objects.filter(username__icontains = search)

    data = [ user.username for user in users ]
    
    return HttpResponse(simplejson.dumps(data))
#enddef#enddef

@secure
def manage(request, userId):
    user = User.objects.get(id=userId)
    availableGroups = Group.objects.all()

    selected = request.session.get("selected", 0)
    if "selected" in request.session: del request.session['selected']

    if request.method == "POST":
        if "overviewForm" in request.POST:
            overviewForm = UserOverviewForm(request.POST, instance=user)

            if overviewForm.is_valid():
                user = overviewForm.save()
            #endif
            request.session['selected'] = 0
        elif "groupsForm" in request.POST:

            # Add group
            groupId = request.POST['addGroup']
            if len(groupId):
                group = Group.objects.get(id=int(groupId))
                user.groups.add(group)
            #endif

            # Remove selected groups
            groupsToRemove = []
            for userGroup in user.groups.all():
                if "group_%s" % userGroup.id in request.POST:
                    groupsToRemove.append(userGroup)
                #endif
            #endif
            if len(groupsToRemove): user.groups.remove(*groupsToRemove)

            request.session['selected'] = 1             # JS - nastav aktivnu zalozku
        #endif

        # Redirect back on manage user page
        return HttpResponseRedirect(
            reverse("accounts:user_manage", kwargs={ "userId": user.id })
        )
    else:
        overviewForm = UserOverviewForm(instance=user)
    #endif

    return render_to_response(
        "accounts/user/manage.html", 
        {
            "managedUser":      user,
            "overviewForm":     overviewForm,
            "availableGroups":  availableGroups,
            "selected":         selected
        }, 
        context_instance=RequestContext(request)
    ) 
#enddef

@secure
def remove(request, userId):
    user = User.objects.get(id=userId)

    if request.method == "POST":
        if "yes" in request.POST and user.id == int(request.POST['userId']):
            user.delete()
        #endif

        return HttpResponseRedirect(
            reverse("accounts:user_remove__select")
        )
    #endif

    return render_to_response(
        "accounts/user/remove.html",
        {
            "managedUser":     user
        },
        context_instance=RequestContext(request)
    )


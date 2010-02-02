# -*- coding: UTF-8 -*-

from django.shortcuts           import render_to_response
from django.contrib.auth.forms  import UserCreationForm
from django.contrib.auth.models import User, Group
from django.template            import RequestContext
from django.http                import HttpResponseRedirect, HttpResponse
from django.utils               import simplejson
from django.core.urlresolvers   import reverse
from django.core.paginator      import Paginator, InvalidPage, EmptyPage

from webPyVirt.decorators       import secure

from forms                      import SelectUserForm, UserOverviewForm, AddGroupForm, SelectGroupForm

@secure
def addUser(request):
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
        "accounts/addUser_Form.html", 
        {
            "form":     form
        }, 
        context_instance=RequestContext(request)
    ) 
#enddef

@secure
def selectUser(request, next):
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
        "accounts/selectUser_Form.html", 
        {
            "users":    users,
            "form":     form,
            "next":     next
        }, 
        context_instance=RequestContext(request)
    ) 
#enddef

@secure
def manageUsers_user(request, userId):
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
            reverse("accounts:manage_users__user", kwargs={ "userId": user.id })
        )
    else:
        overviewForm = UserOverviewForm(instance=user)
    #endif

    return render_to_response(
        "accounts/manageUsers_user.html", 
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
def selectUser_autocomplete(request):
    search = request.GET['term']

    users = User.objects.filter(username__icontains = search)

    data = [ user.username for user in users ]
    
    return HttpResponse(simplejson.dumps(data))
#enddef

@secure
def addGroup(request):
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
        "accounts/addGroup_Form.html", 
        {
            "form":     form
        }, 
        context_instance=RequestContext(request)
    ) 
#enddef

@secure
def selectGroup(request, next):
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

            group = Group.objects.get(name=form.cleaned_data['name'])

            return HttpResponseRedirect(
                reverse(next, kwargs={ "groupId": group.id })
            )
        #endif
    else:
        form = SelectGroupForm()
    #endif

    return render_to_response(
        "accounts/selectGroup_Form.html", 
        {
            "groups":   groups,
            "form":     form,
            "next":     next
        }, 
        context_instance=RequestContext(request)
    ) 
#enddef

@secure
def manageGroups_group(request, groupId):
    group = Group.objects.get(id=groupId)
    availableUsers = User.objects.all().order_by("username")

    selected = request.session.get("selected", 0)
    if "selected" in request.session: del request.session['selected']

    if request.method == "POST":
        if "membersForm" in request.POST:

            if "addUser" in request.POST and len(request.POST['addUser']):
                user = User.objects.get(id=int(request.POST['addUser']))
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
            reverse("accounts:manage_groups__group", kwargs={ "groupId": group.id })
        )

        #endif
    else:
        pass
    #endif

    return render_to_response(
        "accounts/manageGroups_group.html", 
        {
            "managedGroup":     group,
            "availableUsers":   availableUsers,
            "selected":         selected
        }, 
        context_instance=RequestContext(request)
    ) 
#enddef

@secure
def selectGroup_autocomplete(request):
    search = request.GET['term']

    groups = Group.objects.filter(name__icontains = search)

    data = [ group.name for group in groups ]
    
    return HttpResponse(simplejson.dumps(data))
#enddef

@secure
def removeGroup(request, groupId):
    group = Group.objects.get(id=groupId)

    if request.method == "POST":
        if "yes" in request.POST and group.id == int(request.POST['groupId']):
            group.delete()
        #endif

        return HttpResponseRedirect(
            reverse("accounts:remove_group__select_group")
        )
    #endif

    return render_to_response(
        "accounts/removeGroup.html",
        {
            "managedGroup":     group
        },
        context_instance=RequestContext(request)
    )
#enddef

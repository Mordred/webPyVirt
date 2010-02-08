# -*- coding: UTF-8 -*-

from django.shortcuts           import render_to_response, get_object_or_404
from django.template            import RequestContext
from django.http                import HttpResponseRedirect
from django.core.urlresolvers   import reverse
from django.contrib.auth.models import User, Group, Permission

from webPyVirt.decorators       import secure, permissions

from webPyVirt.accounts.forms   import GlobalPermissionsForm

@secure
@permissions("auth.change_permission")
def user(request, userId):
    managedUser = get_object_or_404(User, id=userId)

    permissions = [ perm.codename for perm in managedUser.user_permissions.all() ]
    if managedUser.is_superuser:
        permissions.append("is_superuser")
    #endif

    if request.method == "POST":
        form = GlobalPermissionsForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            if request.user.is_superuser:
                managedUser.is_superuser = data['is_superuser']
            #endif

            toAdd = []
            toRemove = []

            for field in data:
                if data[field]:
                    toAdd.append(field)
                else:
                    toRemove.append(field)
                #endif
            #endfor

            # This permissions we add to user
            toAddPerms = [ perm for perm in Permission.objects.filter(codename__in=toAdd) ]
            managedUser.user_permissions.add(*toAddPerms)

            # This permissions we remove from user
            toRemovePerms = [ perm for perm in Permission.objects.filter(codename__in=toRemove) ]
            managedUser.user_permissions.remove(*toRemovePerms)

            managedUser.save()

            # Redirect back on manage user page
            return HttpResponseRedirect(
                reverse("accounts:permissions_user", kwargs={ "userId": managedUser.id })
            )
        #endif
    else:
        form = GlobalPermissionsForm()
        initial = {}
        for field in form.fields:
            initial[field] = bool(field in permissions)
        #endfor
        form.initial = initial
    #endif

    return render_to_response(
        "accounts/permissions/user.html",
        {
            "managedUser":      managedUser,
            "form":             form
        },
        context_instance=RequestContext(request)
    )
#enddef

@secure
@permissions("auth.change_permission")
def group(request, groupId):
    managedGroup = get_object_or_404(Group, id=groupId)

    permissions = [ perm.codename for perm in managedGroup.permissions.all() ]

    if request.method == "POST":
        form = GlobalPermissionsForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            toAdd = []
            toRemove = []

            for field in data:
                if data[field]:
                    toAdd.append(field)
                else:
                    toRemove.append(field)
                #endif
            #endfor

            # This permissions we add to group
            toAddPerms = [ perm for perm in Permission.objects.filter(codename__in=toAdd) ]
            managedGroup.permissions.add(*toAddPerms)

            # This permissions we remove from group
            toRemovePerms = [ perm for perm in Permission.objects.filter(codename__in=toRemove) ]
            managedGroup.permissions.remove(*toRemovePerms)

            managedGroup.save()

            # Redirect back on manage user page
            return HttpResponseRedirect(
                reverse("accounts:permissions_group", kwargs={ "groupId": managedGroup.id })
            )
        #endif
    else:
        form = GlobalPermissionsForm()

        # Groups doesn't have superuser permission
        form.fields.pop("is_superuser", "")

        initial = {}
        for field in form.fields:
            initial[field] = bool(field in permissions)
        #endfor
        form.initial = initial
    #endif

    return render_to_response(
        "accounts/permissions/group.html",
        {
            "managedGroup":      managedGroup,
            "form":             form
        },
        context_instance=RequestContext(request)
    )
#enddef

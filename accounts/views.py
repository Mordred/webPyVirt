# -*- coding: UTF-8 -*-

from django.shortcuts           import render_to_response
from django.contrib.auth.forms  import UserCreationForm
from django.contrib.auth.models import User
from django.template            import RequestContext
from django.http                import HttpResponseRedirect, HttpResponse
from django.utils               import simplejson
from django.core.urlresolvers   import reverse

from webPyVirt.decorators       import secure

from forms                      import SelectUserForm, UserOverviewForm

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
def manageUsers_selectUser(request):
    if request.method == "POST":
        form = SelectUserForm(request.POST)
        if form.is_valid():

            user = User.objects.get(username=form.cleaned_data['username'])

            return HttpResponseRedirect(
                reverse("accounts:manage_users__user", kwargs={ "userId": user.id })
            )
        #endif
    else:
        form = SelectUserForm()
    #endif

    return render_to_response(
        "accounts/manageUsers_selectUser_Form.html", 
        {
            "form":   form
        }, 
        context_instance=RequestContext(request)
    ) 
#enddef

@secure
def manageUsers_user(request, userId):
    user = User.objects.get(id=userId)

    if request.method == "POST":
        overviewForm = UserOverviewForm(request.POST, instance=user)
        if overviewForm.is_valid():

            user = overviewForm.save()

            return HttpResponseRedirect(
                reverse("accounts:manage_users__user", kwargs={ "userId": user.id })
            )
        #endif
    else:
        overviewForm = UserOverviewForm(instance=user)
    #endif

    return render_to_response(
        "accounts/manageUsers_user.html", 
        {
            "managedUser":      user,
            "overviewForm":     overviewForm
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

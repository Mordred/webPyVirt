# -*- coding: UTF-8 -*-

from django.contrib.auth.models import User, Group
from django.utils.translation   import ugettext_lazy as _
from django                     import forms

class SelectUserForm(forms.Form):

    username = forms.RegexField(label = _("Select user"), max_length = 30, regex = r"^\w+$",
        help_text = _("Only letters, digits and underscores"),
        error_message = _("This value must contain only letters, numbers and underscores."))

    def clean_username(self):
        username = self.cleaned_data['username']

        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError(_("A user with that username does not exist."))
        #endtry

        return username
    #enddef
#endclass

class UserOverviewForm(forms.ModelForm):

    username = forms.RegexField(label = _("Username"), max_length = 30, regex = r"^\w+$",
        help_text = _("Only letters, digits and underscores"),
        error_message = _("This value must contain only letters, numbers and underscores."))
    password1 = forms.CharField(label=_("Password"), required=False, widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"), required=False, widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "is_active", )
    #endclass

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        #endtry

        if self.instance.id != user.id:
            raise forms.ValidationError(_("A user with that username already exists."))
        else:
            return username
        #endif
    #enddef

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password2
    #enddef

    def save(self, commit=True):
        user = super(UserOverviewForm, self).save(commit=False)
        if self.cleaned_data.get("password1"):
            user.set_password(self.cleaned_data["password1"])
        #endif
        if commit:
            user.save()
        #endif
        return user
    #enddef

#endclass

class AddGroupForm(forms.ModelForm):

    name = forms.RegexField(label = _("Group name"), max_length = 30, regex = r"^\w+$",
        help_text = _("Only letters, digits and underscores"),
        error_message = _("This value must contain only letters, numbers and underscores."))

    class Meta:
        model = Group
        fields = ("name", )
    #endclass

    def clean_name(self):
        name = self.cleaned_data['name']

        try:
            Group.objects.get(name=name)
        except Group.DoesNotExist:
            return name
        #endtry
        raise forms.ValidationError(_("A group with that name already exists."))
    #enddef

#endclass

class SelectGroupForm(forms.Form):

    name = forms.RegexField(label = _("Select group"), max_length = 30, regex = r"^\w+$",
        help_text = _("Only letters, digits and underscores"),
        error_message = _("This value must contain only letters, numbers and underscores."))

    def clean_name(self):
        name = self.cleaned_data['name']

        try:
            Group.objects.get(name=name)
        except Group.DoesNotExist:
            raise forms.ValidationError(_("A group with that name does not exist."))
        #endtry

        return name
    #enddef
#endclass

class GlobalPermissionsForm(forms.Form):

    is_superuser = forms.BooleanField(label = _("Superuser"), required = False,
        help_text = _("User is a superuser. Only superuser can change this"))

    change_permission = forms.BooleanField(label = _("Change permissions"), required = False,
        help_text = _("User can change global permissions of another users"))

    add_user = forms.BooleanField(label = _("Add user"), required = False,
        help_text = _("User can add new user"))
    change_user = forms.BooleanField(label = _("Change user"), required = False,
        help_text = _("User can change information about users"))
    delete_user = forms.BooleanField(label = _("Remove user"), required = False,
        help_text = _("User can remove users"))

    add_group = forms.BooleanField(label = _("Add group"), required = False,
        help_text = _("User can add new group"))
    change_group = forms.BooleanField(label = _("Change group"), required = False,
        help_text = _("User can change group members"))
    delete_group = forms.BooleanField(label = _("Remove group"), required = False,
        help_text = _("User can remove groups"))

    add_node = forms.BooleanField(label = _("Add node"), required = False,
        help_text = _("User can add new node"))

#endclass

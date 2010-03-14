# -*- coding: UTF-8 -*-

from django                         import forms
from django.utils.translation       import ugettext_lazy as _
from django.forms.widgets           import HiddenInput

from webPyVirt.domains.models       import Domain, DomainAcl

class SelectDomainForm(forms.Form):

    name = forms.RegexField(label = _("Select domain"), max_length = 255, regex = r"^[\w\-]+$",
        help_text = _("Only letters, digits and underscores"),
        error_message = _("This value must contain only letters, numbers and underscores."))
    id = forms.IntegerField(label = _("Domain ID"),
        help_text = _("Used if 2 domains have the same name (e.g. Domain-0)"),
        widget = HiddenInput,
        required = False)

    def clean_name(self):
        name = self.cleaned_data['name']

        domains = Domain.objects.filter(name=name)
        if not len(domains):
            raise forms.ValidationError(_("A domain with that name does not exist."))
        #endif

        return name
    #enddef

    def clean_id(self):
        id = self.cleaned_data['id']
        if not id: return id

        try:
            Domain.objects.get(id=id)
        except Domain.DoesNotExist:
            raise forms.ValidationError(_("A domain with that name does not exist."))
        #endtry

        return id
    #enddef
#endclass

class DomainAclForm(forms.ModelForm):

    class Meta:
        model = DomainAcl
        exclude = [ "domain" ]

#endclass

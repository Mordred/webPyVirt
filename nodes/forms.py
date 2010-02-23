# -*- coding: UTF-8 -*-

from django                         import forms
from django.utils.translation       import ugettext_lazy as _

from webPyVirt.nodes.models         import Node, NodeAcl

class NodeForm(forms.ModelForm):

    name = forms.RegexField(label = _("Node Name"), max_length = 255, regex = r"^\w+$",
        help_text = _("Only letters, digits and underscores"),
        error_message = _("This value must contain only letters, numbers and underscores."))

    class Meta:
        model = Node
        exclude = [ "owner" ]

#endclass

class NodeAclForm(forms.ModelForm):

    class Meta:
        model = NodeAcl
        exclude = [ "node" ]

#endclass

class SelectNodeForm(forms.Form):

    name = forms.RegexField(label = _("Select node"), max_length = 255, regex = r"^\w+$",
        help_text = _("Only letters, digits and underscores"),
        error_message = _("This value must contain only letters, numbers and underscores."))

    def clean_name(self):
        name = self.cleaned_data['name']

        try:
            Node.objects.get(name=name)
        except Node.DoesNotExist:
            raise forms.ValidationError(_("A node with that name does not exist."))
        #endtry

        return name
    #enddef
#endclass


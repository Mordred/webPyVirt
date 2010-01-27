# -*- coding: UTF-8 -*-

from django.forms       import ModelForm

import models

class NodeForm(ModelForm):

    class Meta:
        model = models.Node

#endclass

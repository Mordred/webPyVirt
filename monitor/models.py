# -*- coding: UTF-8 -*-

from django.db                      import models
from django.contrib.auth.models     import User, Group
from django.utils.translation       import ugettext_lazy as _

from webPyVirt.domains.models       import Domain
from webPyVirt.libs                 import virtualization

class MonitorConfig(models.Model):
    FLAG_NEVER_START = 0x1
    FLAG_NO_PING     = 0x2

    domain = models.OneToOneField(Domain, primary_key = True)

    start_time = models.DateTimeField(null = True, blank = True,
        verbose_name = _("Time when the monitor started"))

    # If NULL ... monitor will never stop
    end_time = models.DateTimeField(null = True, blank = True,
        verbose_name = _("Time when the monitor will end"))

    update_time = models.DateTimeField(auto_now = True,
        verbose_name = _("Time when the monitor make last update"))

    flags = models.PositiveIntegerField(default = 0,
        verbose_name = _("Config flags"))

    sample_interval = models.PositiveSmallIntegerField(default = 3,
        verbose_name = _("Sampling interval (in secs)"))
#endclass

class Statistics(models.Model):

    domain = models.ForeignKey(Domain)

    datetime = models.DateTimeField(auto_now_add = True,
        verbose_name = _("Statictics time"))

    state = models.SmallIntegerField(null = True, blank = True,
        verbose_name = _("State of the domain"))
    max_memory = models.PositiveIntegerField(verbose_name = _("Maximum memory allowed"))
    memory = models.PositiveIntegerField(verbose_name = _("Memory used by the domain"))
    vcpu = models.PositiveSmallIntegerField(verbose_name = _("Number of virtual CPUs for the domain"))
    cpu_time = models.FloatField(verbose_name = _("CPU time of the domain processor"))

    current_id = models.PositiveIntegerField(null = True, blank = True,
        verbose_name = _("Current running ID"))

    percentage_cpu = models.FloatField(verbose_name = _("CPU usage in \"%\""))
    percentage_memory = models.FloatField(verbose_name = _("Memory usage in \"%\""))
#endclass

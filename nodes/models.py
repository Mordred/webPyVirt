# -*- coding: UTF-8 -*-

from django.db                      import models
from django.contrib.auth.models     import User, Group
from django.utils.translation       import ugettext_lazy as _

try:
    # Python 2.6
    from urlparse   import parse_qs
except ImportError:
    # Python 2.5
    from cgi        import parse_qs
#endtry

from socket         import AF_INET, AF_UNIX

class Node(models.Model):
    DRIVERS = (
        (u"xen", _(u"Xen")),
        (u"qemu", _(u"QEMU / KVM")),
        (u"lxc", _(u"Linux Containers (LXC)")),
        (u"test", _(u"Test \"mock\"")),
        (u"openvz", _(u"OpenVZ")),
        (u"uml", _(u"User Mode Linux")),
        (u"vbox", _(u"VirtualBox")),
        (u"one", _(u"Open Nebula")),
        (u"esx", _(u"VMware ESX")),
        (u"gsx", _(u"VMware GSX"))
    )
    TRANSPORTS = (
        (u"tls", _(u"TLS 1.0 (SSL 3.1)")),
        (u"unix", _(u"Unix domain socket")),
        (u"ssh", _(u"SSH tunneled")),
        (u"ext", _(u"External program")),
        (u"tcp", _(u"Unencrypted TCP/IP socket"))
    )

    name = models.CharField(max_length = 255, verbose_name = _("Node Name"), unique = True)
    owner = models.ForeignKey(User)

    # Node connection
    driver = models.CharField(max_length = 6, choices = DRIVERS,
        verbose_name = _("Hypervisor Driver"))
    address = models.CharField(max_length = 255, null = True, blank = True,
        verbose_name = _("Hostname / IP Address"))
    port = models.IntegerField(null = True, blank = True, verbose_name = _("Port"))
    transport = models.CharField(max_length = 4, choices = TRANSPORTS, null = True, blank = True,
        verbose_name = _("Used Transport"))
    
    username = models.CharField(max_length = 60, null = True, blank = True, verbose_name = _("Username"))
    path = models.CharField(max_length = 1024, null = True, blank = True, verbose_name = _("Path"))
    extra_parameters = models.CharField(max_length = 1024, null = True, blank = True, 
        verbose_name = _("Extra Parameters"))

    def __unicode__(self):
        return self.name
    #enddef

    def getURI(self):
        """
        Generate Libvirt URI format from data
        """
        # Driver
        uri = u"%s" % (self.driver)

        # Transport
        if self.transport: uri += u"+%s" % (self.transport)

        uri += u"://"

        # Username
        if self.username: uri += u"%s@" % (self.username)

        # Hostname / IP address
        if self.address: uri += u"%s" % (self.address)

        # Port
        if self.port: uri += u":%s" % (self.port)

        uri += u"/"

        # Path
        if self.path: uri += u"%s" % (self.path)

        # Extra parameters
        if self.extra_parameters: uri += u"?%s" % (self.extra_parameters)

        return uri
        
    #enddef

    def getHost(self):
        return self.address
    #enddef
    
    def getPort(self):
        if self.port:
            return self.port
        else:
            if not self.transport or self.transport == "tls":
                return 16514
            elif self.transport == "tcp":
                return 16509
            elif self.transport == "ssh":
                return 23
            #endif
        #endif

        return None
    #enddef

    def getAddressForSocket(self):
        if self.transport == "unix":
            qs = parse_qs(self.extra_parameters)
            if "socket" in qs:
                return AF_UNIX, qs['socket'][0]
            else:
                return AF_UNIX, "/var/run/libvirt/libvirt-sock"
            #endif
        else:
            return AF_INET, (self.getHost(), self.getPort())
        #endif
    #enddef

#endclass

class NodeAcl(models.Model):

    node = models.ForeignKey(Node)

    change_acl = models.NullBooleanField(verbose_name = _("Change ACL"),
        help_text = _("User can change ACL for the node"))

    add_domain = models.NullBooleanField(verbose_name = _("Add Domain"),
        help_text = _("User can create new domain on the node"))

    view_node = models.NullBooleanField(verbose_name = _("View Node"),
        help_text = _("User can view the node in the administration"))
    change_node = models.NullBooleanField(verbose_name = _("Change Node"),
        help_text = _("User can change node data"))
    delete_node = models.NullBooleanField(verbose_name = _("Delete Node"),
        help_text = _("User can delete the node"))

    class Meta:
        abstract = True

#endclass

class UserNodeAcl(NodeAcl):

    user = models.ForeignKey(User)

    class Meta:
        unique_together = ("node", "user")

#endclass

class GroupNodeAcl(NodeAcl):

    group = models.ForeignKey(Group)

    class Meta:
        unique_together = ("node", "group")

#endclass

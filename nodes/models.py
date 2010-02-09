# -*- coding: UTF-8 -*-

from django.db                      import models
from django.contrib.auth.models     import User

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
        (u"xen", u"Xen"),
        (u"qemu", u"QEMU / KVM"),
        (u"lxc", u"Linux Containers (LXC)"),
        (u"test", u"Test \"mock\""),
        (u"openvz", u"OpenVZ"),
        (u"uml", u"User Mode Linux"),
        (u"vbox", u"VirtualBox"),
        (u"one", u"Open Nebula"),
        (u"esx", u"VMware ESX"),
        (u"gsx", u"VMware GSX")
    )
    TRANSPORTS = (
        (u"tls", u"TLS 1.0 (SSL 3.1)"),
        (u"unix", u"Unix domain socket"),
        (u"ssh", u"SSH tunneled"),
        (u"ext", u"External program"),
        (u"tcp", u"Unencrypted TCP/IP socket")
    )

    name = models.CharField(max_length = 255, verbose_name = "Node Name", unique = True)
    owner = models.ForeignKey(User)

    # Node connection
    driver = models.CharField(max_length = 6, choices = DRIVERS,
        verbose_name = "Hypervisor Driver")
    address = models.CharField(max_length = 255, null = True, blank = True,
        verbose_name = "Hostname / IP Address")
    port = models.IntegerField(null = True, blank = True, verbose_name = "Port")
    transport = models.CharField(max_length = 4, choices = TRANSPORTS, null = True, blank = True,
        verbose_name = "Used Transport")
    
    username = models.CharField(max_length = 60, null = True, blank = True, verbose_name = "Username")
    path = models.CharField(max_length = 1024, null = True, blank = True, verbose_name = "Path")
    extra_parameters = models.CharField(max_length = 1024, null = True, blank = True, 
        verbose_name = "Extra Parameters")

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

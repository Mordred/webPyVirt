# -*- coding: UTF-8 -*-

import libvirt
import socket
import logging
import sys

import misc

LIST_DOMAINS_ACTIVE     = 0x1
LIST_DOMAINS_INACTIVE   = 0x2

# ----------------------------------------------------------------

class ErrorException(Exception):
    pass
#endclass

class CantConnectException(ErrorException):
    pass
#endclass

class NoPingException(ErrorException):
    pass
#endclass

# ----------------------------------------------------------------

# USAGE @secure
class ping(object):

    def __init__(self, function):
        self.fnc = function
    #enddef

    def __call__(self, node, *args, **kwargs):
        if node.driver == "test":
            return self.fnc(node, *args, **kwargs)
        else:
            # PING before try to connect, because ping has implemented timeout
            family, address = node.getAddressForSocket()
            if not misc.ping(address, family):
                raise NoPingException("Cannot connect to hypervisor!")
            else:
                return self.fnc(node, *args, **kwargs)
            #endif
        #endif
    #enddef

#endclass

# ----------------------------------------------------------------

@ping
def openConnection(node, readOnly = True):
    """
    @returns read-only connection to hypervisor
    """
    error = None
    connection = None

    uri = node.getURI()

    try:
        if readOnly:
            connection = libvirt.openReadOnly(uri)
        else:
            connection = libvirt.open(uri)
        #endif
    except libvirt.libvirtError, e:
        error = unicode(e)
    #endtry

    if not connection and not error:
        error = u"Failed to open connection to the hypervisor"
    #endif

    if error:
        logging.error("libvirt: %s" % error)
        if connection: connection.close()
        raise CantConnectException(error)
    #endif

    return connection
#enddef

# ----------------------------------------------------------------

def testConnection(node):
    """
    @param uri      Node URI
    @returns
        dict       Information about node
            "model":        string      (CPU model)
            "memory":       integer     (in MB)
            "cpus":         integer     (number of active CPUs)
            "mhz":          integer     (CPU frequency)
            "nodes":        integer     (the number of NUMA cell, 1 for uniform mem access)
            "sockets":      integer     (number of CPU socket per node)
            "cores":        integer     (number of core per socket)
            "threads":      integer     (number of threads per core)
    """
    try:
        connection = openConnection(node)
        nodeInfo = connection.getInfo()
    except libvirt.libvirtError, e:
        logging.error("libvirt: %s" % unicode(e))
        raise ErrorException(unicode(e))
    else:
        connection.close()
    #endtry

    return {
        "model":            nodeInfo[0],
        "memory":           nodeInfo[1],
        "cpus":             nodeInfo[2],
        "mhz":              nodeInfo[3],
        "nodes":            nodeInfo[4],
        "sockets":          nodeInfo[5],
        "cores":            nodeInfo[6],
        "threads":          nodeInfo[7]
    }
#enddef

def listDomains(node, listFilter = LIST_DOMAINS_ACTIVE):
    active = []
    inactive = []

    try:
        connection = openConnection(node)
        if listFilter & LIST_DOMAINS_ACTIVE:
            active = [ connection.lookupByID(domId).UUIDString() for domId in connection.listDomainsID() ]
        #endif
        if listFilter & LIST_DOMAINS_INACTIVE:
            inactive = [ connection.lookupByName(domName).UUIDString() for domName in connection.listDefinedDomains() ]
        #endif
    except libvirt.libvirtError, e:
        logging.error("libvirt: %s" % unicode(e))
        raise ErrorException(unicode(e))
    else:
        connection.close()
    #endtry

    return active + inactive
#enddef

def getDomainXML(node, domainUUID):
    try:
        connection = openConnection(node, False)
        domain = connection.lookupByUUIDString(domainUUID)
        xml = domain.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE | libvirt.VIR_DOMAIN_XML_INACTIVE)
    except libvirt.libvirtError, e:
        logging.error("libvirt: %s" % unicode(e))
        raise ErrorException(unicode(e))
    else:
        connection.close()
    #endtry

    return xml
#enddef


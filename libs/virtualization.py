# -*- coding: UTF-8 -*-

import libvirt
import socket
import logging

from misc   import ping

TIMEOUT = 5

def testConnection(node, timeout = TIMEOUT):
    """
    @param uri      Node URI
    @returns dict result
        "success":      boolean
        "error":        string  (if success == False)  (error message)
        "info":         dict    (if success == True)   (information about node)
                            "model":        string      (CPU model)
                            "memory":       integer     (in KB)
                            "cpus":         integer     (number of active CPUs)
                            "mhz":          integer     (CPU frequency)
                            "nodes":        integer     (the number of NUMA cell, 1 for uniform mem access)
                            "sockets":      integer     (number of CPU socket per node)
                            "cores":        integer     (number of core per socket)
                            "threads":      integer     (number of threads per core)
    """
    error = None
    connection = None

    if node.driver == "test":
        # To test driver we have always connection
        canConnect = True
    else:
        # PING before try to connect, because ping has implemented timeout
        family, address = node.getAddressForSocket()
        canConnect = ping(address, family)
    #endif

    if canConnect:
        uri = node.getURI()

        try:
            connection = libvirt.openReadOnly(uri)
        except libvirt.libvirtError, e:
            error = unicode(e)
        #endtry
    else:
        error = "Cannot connect to host"
    #endif

    if not connection and not error:
        error = "Failed to open connection to the hypervisor"
    #endif

    if error:
        logging.error("libvirt: %s" % error)
        if connection: connection.close()
        return {
            "success":      False,
            "error":        error
        }
    #endif

    nodeInfo = connection.getInfo()

    connection.close()
    return {
        "success":          True,
        "info":             {
            "model":            nodeInfo[0],
            "memory":           nodeInfo[1],
            "cpus":             nodeInfo[2],
            "mhz":              nodeInfo[3],
            "nodes":            nodeInfo[4],
            "sockets":          nodeInfo[5],
            "cores":            nodeInfo[6],
            "threads":          nodeInfo[7]
        }
    }
#enddef

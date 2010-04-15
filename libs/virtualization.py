# -*- coding: UTF-8 -*-

import libvirt
import socket
import logging
import sys

import misc
import parse

LIST_DOMAINS_ACTIVE     = 0x1
LIST_DOMAINS_INACTIVE   = 0x2

LIST_POOLS_ACTIVE       = 0x1
LIST_POOLS_INACTIVE     = 0x2

STORAGE_VOL_FILE        = 0
STORAGE_VOL_BLOCK       = 1

DOMAIN_STATE_NOSTATE    = 0
DOMAIN_STATE_RUNNING    = 1
DOMAIN_STATE_BLOCKED    = 2
DOMAIN_STATE_PAUSED     = 3
DOMAIN_STATE_SHUTDOWN   = 4
DOMAIN_STATE_SHUTOFF    = 5
DOMAIN_STATE_CRASHED    = 6

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

# USAGE @ping
def ping(method):

    def decorator(virNode, *args, **kwargs):
        if virNode.node.driver == "test":
            return method(virNode, *args, **kwargs)
        else:
            # PING before try to connect, because ping has implemented timeout
            family, address = virNode.node.getAddressForSocket()
            if not misc.ping(address, family):
                raise NoPingException("Cannot connect to hypervisor!")
            else:
                return method(virNode, *args, **kwargs)
            #endif
        #endif
    #enddef

    return decorator

#enddef

# ----------------------------------------------------------------

class virNode(object):

    def __init__(self, node):
        if not node: raise ValueError("Node not set")

        self.node = node

        # Variables
        self.readOnly = None

        # Connection
        self._connection = None
    #enddef

    def __del__(self):
        if self._connection: self._connection.close()
    #enddef

    @ping
    def getConnection(self, readOnly = False):
        if not self._connection or self.readOnly != readOnly:
            if self._connection: self._connection.close()

            self._connection = None
            error = None

            uri = self.node.getURI()

            try:
                if readOnly:
                    self._connection = libvirt.openReadOnly(uri)
                else:
                    self._connection = libvirt.open(uri)
                #endif
            except libvirt.libvirtError, e:
                error = unicode(e)
            #endtry

            if not self._connection and not error:
                error = u"Failed to open connection to the hypervisor"
            #endif

            if error:
                logging.error("libvirt: %s" % error)
                if self._connection: self._connection.close()
                self._connection = None
                raise CantConnectException(error)
            #endif

            self.readOnly = readOnly
            return self._connection
        else:
            return self._connection
        #endif
    #enddef

    def getInfo(self):
        """
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
            connection = self.getConnection()
            nodeInfo = connection.getInfo()
        except libvirt.libvirtError, e:
            logging.error("libvirt: %s" % unicode(e))
            raise ErrorException(unicode(e))
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

    def getFreeMemory(self):
        try:
            connection = self.getConnection()
            freeMemory = connection.getFreeMemory()
        except libvirt.libvirtError, e:
            logging.error("libvirt: %s" % unicode(e))
            raise ErrorException(unicode(e))
        #endtry

        return freeMemory
    #enddef

    def listDomains(self, listFilter = LIST_DOMAINS_ACTIVE):
        active = []
        inactive = []

        try:
            connection = self.getConnection()
            if listFilter & LIST_DOMAINS_ACTIVE:
                active = [ connection.lookupByID(domId).UUIDString() for domId in connection.listDomainsID() ]
            #endif
            if listFilter & LIST_DOMAINS_INACTIVE:
                inactive = [ connection.lookupByName(domName).UUIDString()
                    for domName in connection.listDefinedDomains() ]
            #endif
        except libvirt.libvirtError, e:
            logging.error("libvirt: %s" % unicode(e))
            raise ErrorException(unicode(e))
        #endtry

        return active + inactive
    #enddef

    def listStoragePools(self, listFilter = LIST_POOLS_ACTIVE):
        active = []
        inactive = []

        try:
            connection = self.getConnection()
            if listFilter & LIST_POOLS_ACTIVE:
                active = connection.listStoragePools()
            #endif
            if listFilter & LIST_POOLS_INACTIVE:
                inactive = connection.listDefinedStoragePools()
            #endif
        except libvirt.libvirtError, e:
            logging.error("libvirt: %s" % unicode(e))
            raise ErrorException(unicode(e))
        #endtry

        return active + inactive
    #enddef

    def getDomain(self, uuid):
        try:
            connection = self.getConnection()
            return virDomain(node = self, connection = connection.lookupByUUIDString(uuid))
        except libvirt.libvirtError, e:
            logging.error("libvirt: %s" % unicode(e))
            raise ErrorException(unicode(e))
        #endtry
    #enddef

    def getDomainConnection(self, model):
        try:
            connection = self.getConnection()
            return connection.lookupByUUIDString(model.uuid)
        except libvirt.libvirtError, e:
            logging.error("libvirt: %s" % unicode(e))
            raise ErrorException(unicode(e))
        #endtry
    #enddef

    def createStoragePool(self, xml):
        try:
            connection = self.getConnection()
            storagePool = connection.storagePoolDefineXML(xml, 0)
            storagePool.build(0)
            storagePool.setAutostart(1)
            storagePool.create(0)
            info = storagePool.info()
        except libvirt.libvirtError, e:
            logging.error("libvirt: %s" % unicode(e))
            raise ErrorException(unicode(e))
        #endtry

        return {
            "state":        info[0],
            "capacity":     info[1],
            "allocation":   info[2],
            "available":    info[3]
        }
    #enddef

    def createStorageVolume(self, poolName, xml):
        try:
            connection = self.getConnection()
            storagePool = connection.storagePoolLookupByName(poolName)
            storagePool.createXML(xml, 0)
        except libvirt.libvirtError, e:
            logging.error("libvirt: %s" % unicode(e))
            raise ErrorException(unicode(e))
        #endtry

        return True
    #enddef

    # Chcelo by to vlastnu triedu
    def getStoragePoolInfo(self, poolName):
        try:
            connection = self.getConnection()
            storagePool = connection.storagePoolLookupByName(poolName)
            info = storagePool.info()
        except libvirt.libvirtError, e:
            logging.error("libvirt: %s" % unicode(e))
            raise ErrorException(unicode(e))
        #endtry

        return {
            "state":        info[0],
            "capacity":     info[1],
            "allocation":   info[2],
            "available":    info[3]
        }
    #enddef

    # Chcelo by to vlastnu triedu
    def listStorageVolumes(self, poolName):
        try:
            connection = self.getConnection()
            storagePool = connection.storagePoolLookupByName(poolName)
            storagePool.refresh(0)
            volumes = storagePool.listVolumes()
        except libvirt.libvirtError, e:
            logging.error("libvirt: %s" % unicode(e))
            raise ErrorException(unicode(e))
        #endtry

        return volumes
    #enddef

    def listNetworks(self):
        try:
            connection = self.getConnection()
            networks = connection.listNetworks()
        except libvirt.libvirtError, e:
            logging.error("libvirt: %s" % unicode(e))
            raise ErrorException(unicode(e))
        #endtry

        return networks
    #enddef

    # Chcelo by to vlastnu triedu
    def getStorageVolumeInfo(self, poolName, volumeName):
        try:
            connection = self.getConnection()
            storagePool = connection.storagePoolLookupByName(poolName)
            storagePool.refresh(0)
            volume = storagePool.storageVolLookupByName(volumeName)
            info = volume.info()
            path = volume.path()
        except libvirt.libvirtError, e:
            logging.error("libvirt: %s" % unicode(e))
            raise ErrorException(unicode(e))
        #endtry

        return {
            "type":         info[0],
            "capacity":     info[1],
            "allocation":   info[2],
            "path":         path
        }
    #enddef

#endclass

# ----------------------------------------------------------------

class virDomain(object):

    def __init__(self, model = None, node = None, connection = None):
        if not model and not connection: raise ValueError("Model or connection must be set")

        # Variables
        self.xml = None
        self.devices = None

        # Internal
        self._model = model
        self._connection = connection
        self._node = node
    #enddef

    def __del__(self):
        if self._connection: del self._connection
    #enddef

    def getConnection(self):
        if self._connection: return self._connection

        model = self.getModel()

        node = self.getNode()
        self._connection = node.getDomainConnection(model)

        return self._connection
    #enddef

    def getNode(self):
        if self._node: return self._node

        model = self.getModel()
        if not self._node: self._node = virNode(model.node)
        return self._node
    #enddef

    def getXML(self, renew = False):
        if self.xml and not renew: return self.xml

        con = self.getConnection()
        try:
            self.xml = con.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE)
        except libvirt.libvirtError, e:
            logging.error("libvirt: %s" % unicode(e))
            raise ErrorException(unicode(e))
        #endtry

        return self.xml
    #enddef

    def getModel(self, renew = False):
        if self._model and not renew: return self._model

        con = self.getConnection()
        xml = self.getXML()

        self._model, self.devices = parse.parseDomainXML(xml)

        # XEN in dumpxml gives bad data about memory for Domain-0
        # so set max memory to host memory
        if con.ID() == 0 and self._model.hypervisor_type == "xen":
            node = self.getNode()
            info = node.getInfo()
            self._model.memory = info["memory"] * 1024
        #endif

        return self._model
    #enddef

    def getDevices(self, renew = False):
        if self.devices and not renew: return self.devices

        if self._model and not renew:
            self.devices = self._model.getDevices()
        else:
            con = self.getConnection()
            xml = self.getXML()
            model, self.devices = parse.parseDomainXML(xml)
        #endif

        return self.devices
    #enddef

    def saveModel(self, owner = None, node = None):
        model = self.getModel()
        devices = self.getDevices()

        if (not owner and not model.owner) \
            or (not node and not model.node): raise ValueError("Owner or node must be set")

        if not model.owner: model.owner = owner
        if not model.node: model.node = node

        model.save()
        for devType, devs in devices.items():
            for device in devs:
                device.domain = domain
                device.save()
            #endfor
        #endfor
    #enddef

    def getInfo(self):
        con = self.getConnection()

        try:
            info = con.info()
            if info[1] == -1:           # Max memory not set ... so get memory from node
                node = self.getNode()
                nodeInfo = node.getInfo()
                info[1] = nodeInfo['memory'] * 1024
            #endif
        except libvirt.libvirtError, e:
            logging.error("libvirt: %s" % unicode(e))
            raise ErrorException(unicode(e))
        #endtry

        return {
            "state":        info[0],
            "maxMemory":    info[1],
            "memory":       info[2],
            "vcpu":         info[3],
            "cpuTime":      info[4]
        }
    #enddef

    def getState(self):
        info = self.getInfo()
        return info['state']
    #enddef

    def suspend(self):
        con = self.getConnection()

        try:
            con.suspend()
        except libvirt.libvirtError, e:
            logging.error("libvirt: %s" % unicode(e))
            raise ErrorException(unicode(e))
        #endtry

        return True
    #enddef

    def resume(self):
        con = self.getConnection()

        try:
            con.resume()
        except libvirt.libvirtError, e:
            logging.error("libvirt: %s" % unicode(e))
            raise ErrorException(unicode(e))
        #endtry

        return True
    #enddef

    def shutdown(self):
        con = self.getConnection()

        try:
            con.shutdown()
        except libvirt.libvirtError, e:
            logging.error("libvirt: %s" % unicode(e))
            raise ErrorException(unicode(e))
        #endtry

        return True
    #enddef

    def reboot(self):
        con = self.getConnection()

        try:
            con.reboot(0)
        except libvirt.libvirtError, e:
            logging.error("libvirt: %s" % unicode(e))
            raise ErrorException(unicode(e))
        #endtry

        return True
    #enddef

    def destroy(self):
        con = self.getConnection()

        try:
            con.destroy()
        except libvirt.libvirtError, e:
            logging.error("libvirt: %s" % unicode(e))
            raise ErrorException(unicode(e))
        #endtry

        return True
    #enddef

    def ID(self):
        con = self.getConnection()

        try:
            con.ID()
        except libvirt.libvirtError, e:
            logging.error("libvirt: %s" % unicode(e))
            raise ErrorException(unicode(e))
        #endtry

        return True
    #enddef

    def setVCPUs(self, vcpus):
        con = self.getConnection()

        try:
            con.setVcpus(vcpus)
            vcpu = self.getInfo()['vcpu']
        except libvirt.libvirtError, e:
            logging.error("libvirt: %s" % unicode(e))
            raise ErrorException(unicode(e))
        #endtry

        model = self.getModel()
        model.vcpu = vcpu
        model.save()
        return True
    #enddef

    def setMaxMemory(self, memory):
        con = self.getConnection()

        try:
            con.setMaxMemory(memory)
            maxMemory = self.getInfo()['maxMemory']
        except libvirt.libvirtError, e:
            logging.error("libvirt: %s" % unicode(e))
            raise ErrorException(unicode(e))
        #endtry

        model = self.getModel()
        model.memory = maxMemory
        model.save()
        return True
    #enddef

    def setMemory(self, memory):
        con = self.getConnection()

        try:
            con.setMemory(memory)
            memory = self.getInfo()['memory']
        except libvirt.libvirtError, e:
            logging.error("libvirt: %s" % unicode(e))
            raise ErrorException(unicode(e))
        #endtry

        model = self.getModel()
        model.memory_current = memory
        model.save()
        return True
    #enddef

    def save(self):
        raise NotImplementedError
    #enddef

#endclass

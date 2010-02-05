# -*- coding: UTF-8 -*-

import socket

TIMEOUT = 2

def ping(address, family = socket.AF_INET, timeout = TIMEOUT):
    """
    Ping host:port
    """
    sock = socket.socket(family, socket.SOCK_STREAM)
    sock.settimeout(timeout)

    try:
        sock.connect(address)
    except Exception, e:
        return False
    else:
        sock.close()
    #endtry

    return True
#enddef


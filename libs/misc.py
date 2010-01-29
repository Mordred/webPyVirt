# -*- coding: UTF-8 -*-

import signal

class TimeoutException(Exception):
    pass
#endclass

class TimeoutFunction(Exception):

    def __init__(self, function, timeout):
        self.function = function
        self.timeout = timeout
    #enddef

    def handle_timeout(self, signum, frame):
        raise TimeoutException()
    #enddef

    def __call__(self, *args):

        old = signal.signal(signal.SIGALRM, self.handle_timeout)

        signal.alarm(self.timeout)

        try:
            result = self.function(*args)
        finally:
            signal.signal(signal.SIGALRM, old)
        #endtry

        signal.alarm(0)

        return result
    #enddef
#endclass


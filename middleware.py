# -*- coding: UTF-8 -*-

from django.conf    import settings

import logging

class DebugSQLMiddleware(object):

    def process_response(self, request, response):

        if settings.DEBUG and request.META.get("REMOTE_ADDR") in settings.INTERNAL_IPS:
            from django.db import connection

            logging.debug(request.path)

            for sql in connection.queries:
                logging.debug("%s (time %ss)" % (sql['sql'], sql['time']))
            #endfor
        #endif

        return response
    #enddef

#endclass

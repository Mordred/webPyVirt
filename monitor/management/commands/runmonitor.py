# -*- coding: UTF-8 -*-
import logging
from optparse import make_option

from django.core.management.base    import NoArgsCommand

from webPyVirt.monitor.monitor      import Monitor

class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option("--no-daemon", action="store_false", dest="daemon",
            default=True,
            help="Do not daemonize the monitor."),
    )
    help = "Runs webPyVirt monitor which collect data from domains and store it in database."

    requires_model_validation = False

    def handle_noargs(self, **options):
        daemon = options.get("daemon", True)

        try:
            monitor = Monitor(daemon)
            monitor.run()
        except Exception, e:
            import traceback
            logging.debug("Monitor exception:\n%s" % (traceback.format_exc()))
            print unicode(e)
        #endtry

    #enddef

#endclass


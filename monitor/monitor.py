# -*- coding: UTF-8 -*-

import logging, os, sys, errno, time, datetime

from django.conf                import settings
from django.db                  import transaction

from webPyVirt.domains.models   import Domain
from webPyVirt.monitor.models   import MonitorConfig, Statistics
from webPyVirt.monitor.threads  import DomainMonitor

class MonitorException(Exception):
    pass
#endclass

class Monitor(object):
    """
    Process which will run threads for monitoring remote domains
    """

    def __init__(self, daemon = True, lifetime = None):
        self.daemon = daemon
        self.lifetime = lifetime
        self.startTime = datetime.datetime.now()

        # Internal variables
        self._monitors = {}
    #enddef

    def __del__(self):
        pass
    #enddef

    def daemonize(self, outLog = "/dev/null", errLog = "/dev/null", umask = 022, chroot = None):
        """
        Turn process into a LINUX daemon
        """
        # First fork
        try:
            if os.fork() > 0:
                sys.exit(0)     # Kill parent
            #endif
        except OSError, e:
            message = "Monitor: Fork failed (%d, %s)" % (e.errno, e.strerror)
            logging.debug(message)
            raise MonitorException(message)
        #endtry

        # Run in new session
        os.setsid()

        if chroot:
            # Switch to chroot directory
            os.chdir(chroot)
        #endif

        os.umask(umask)

        # Second fork
        try:
            if os.fork() > 0:
                os._exit(0)
            #endif
        except OSError, e:
            logging.debug("Monitor: Fork #2 failed (%d, %s)" % (e.errno, e.strerror))
            os._exit(1)
        #endtry

        si = open("/dev/null", "r")
        so = open(outLog, "a+", 0)
        se = open(errLog, "a+", 0)

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # Set custom filedescriptors so that they get proper buffering
        sys.stdout, sys.stderr = so, se
    #enddef

    def readPID(self):
        pidFile = settings.MONITOR_PID

        if not os.path.exists(pidFile):
            return 0
        #endif

        try:
            fd = open(pidFile)
        except IOError, e:
            message = "Monitor: Can't open pid file `%s` (reason: %s)." \
                % (pidFile, os.strerror(e[0]))
            logging.error(message)
            raise MonitorException(message)
        #endtry

        pid = fd.readline()
        fd.close()

        return len(pid) > 0 and int(pid) or 0
    #enddef

    def isRunning(self):
        """
        Test if monitor not running
        """
        pidFile = settings.MONITOR_PID
        othPid = self.readPID()

        running = False

        if othPid:
            try:
                os.kill(othPid, 0)          # Check the process
            except OSError, e:
                if e[0] != errno.ESRCH: running = True
            else:
                running = True
            #endtry

            if running:
                message = "Already running under pid `%d`" % (othPid)
                logging.critical(message)
                return True
            #endif

            logging.warning("Pid file `%s` with `%d` found. Unclean shutdown of previous monitor run?" \
                % (pidFile, othPid))

            self.removePID()
        #endif

        return running
    #enddef

    def writePID(self):
        pidFile = settings.MONITOR_PID

        try:
            fd = open(pidFile, "w")
            fd.write(str(os.getpid()))
            fd.close()
        except IOError, e:
            message = "Can't create pid file `%s` (reason: %s)" % (pidFile, e.strerror)
            logging.critical(message)
            raise MonitorException(message)
        #endtry
    #enddef

    def removePID(self):
        pidFile = settings.MONITOR_PID

        try:
            os.remove(pidFile)
        except IOError, e:
            message = "Can't remove stale pid file `%s` (reason: %s)" % (pidFile, e.strerror)
            logging.critical(message)
            raise MonitorException(message)
        #endtry
    #enddef

    def run(self):

        # Test if monitor is running
        if self.isRunning(): raise MonitorException("Already running under pid `%d`" % (self.readPID()))

        if self.daemon:
            logging.info("Monitor: Forking to background.")
            try:
                self.daemonize()
            except Exception, e:
                import traceback
                message = "Monitor: Daemonization failed:\n%s" % (traceback.format_exc())
                logging.critical(message)
                raise # Re-raise
            #endtry
        #endif

        self.writePID()

        # MAIN PROCESS
        self._run()

        self.removePID()
    #enddef

    # We need to commit manually because django commit after function end
    # so the _query_set_.get() would return always the same
    @transaction.commit_manually
    def _run(self):

        allDone = False

        while not allDone:

            # Get all domains
            domains = Domain.objects.all()

            # For every domain
            for domain in domains:

                # Skip if thread already running
                if domain.id in self._monitors:
                    if self._monitors[domain.id].isAlive():
                        continue
                    else:
                        del self._monitors[domain.id]
                    #endif
                #endif

                try:
                    config = domain.monitorconfig
                except MonitorConfig.DoesNotExist:
                    config = None
                #endtry

                if not config or (config.end_time and config.end_time < self.startTime):
                    if self.lifetime:
                        end = datetime.datetime.fromtimestamp(time.time() + self.lifetime)
                    else:
                        end = None
                    #endif

                    if not config:
                        config = MonitorConfig(domain=domain, end_time=end)
                    else:
                        config.end_time = end
                        config.flags &= ~MonitorConfig.FLAG_NO_PING
                    #endif

                    config.save()
                    transaction.commit()
                #endif

                # Skip if NEVER_START flag is set
                if config.flags & MonitorConfig.FLAG_NEVER_START: continue

                # Skip if NO_PING flag is set and update_time < now for 5 min
                if config.flags & MonitorConfig.FLAG_NO_PING and \
                    (datetime.datetime.now() - config.update_time) < datetime.timedelta(minutes=5):
                    continue
                else:
                    config.flags &= ~MonitorConfig.FLAG_NO_PING
                    config.save()
                    transaction.commit()
                #endif

                # Skip if end_time < now
                if config.end_time and datetime.datetime.now() > config.end_time: continue

                monitorThread = DomainMonitor(domain)
                monitorThread.daemon = True
                monitorThread.start()

                self._monitors[domain.id] = monitorThread

            #endfor

            if len(self._monitors):
                time.sleep(5)       # Sleep for 5 secs
            else:
                allDone = True      # All domains done
            #endif

            # Remove data older than 1 day
            # If somebody want to make history data can be stored
            # from database to disk, but this is not our problem ;)
            self.cleanUpStatistics()
            transaction.commit()
        #endwhile

    #enddef

    def cleanUpStatistics(self, maxTime = 28800):
        movingWall = datetime.datetime.fromtimestamp(time.time() - maxTime)
        Statistics.objects.filter(datetime__lt=movingWall).delete()
    #enddef

#endclass

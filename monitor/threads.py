# -*- coding: UTF-8 -*-

import threading, datetime, time, logging

from django.db                      import transaction

from webPyVirt.monitor.models       import MonitorConfig, Statistics
from webPyVirt.libs                 import virtualization

class DomainMonitor(threading.Thread):

    def __init__(self, domain):
        threading.Thread.__init__(self)

        self.domain = domain
        self.time = None
        self.cpuTime = None
        self.cores = None

        self.virDomain = virtualization.virDomain(domain)
    #endclass

    def __del__(self):
        del self.virDomain
    #enddef

    @transaction.commit_manually
    def run(self):

        # Update Start time
        config = MonitorConfig.objects.get(domain=self.domain)
        config.start_time = datetime.datetime.now()
        config.save()
        transaction.commit()

        finished = False

        try:
            # Check number of cores on the node
            self.cores = self.virDomain.getNode().getInfo()['cores']

            while not finished:
                config = MonitorConfig.objects.get(domain=self.domain)
                config.save()
                transaction.commit()

                info = self.virDomain.getInfo()

                newTime = time.time()

                if self.time and self.cpuTime:
                    stats = Statistics(domain = self.domain)
                    stats.state = info['state']
                    stats.max_memory = info['maxMemory']
                    stats.memory = info['memory']
                    stats.vcpu = info['vcpu']
                    stats.cpu_time = info['cpuTime']
                    stats.current_id = self.virDomain.ID()

                    stats.percentage_cpu = self.calculateCPUUsage(time.time() - self.time, info['cpuTime'] - self.cpuTime)
                    stats.percentage_memory = 100 * float(info['memory']) / float(info['maxMemory'])

                    stats.save()
                    transaction.commit()
                #endif

                self.cpuTime = info['cpuTime']
                self.time = newTime

                # Test if we are finished
                if config.end_time and datetime.datetime.now() > config.end_time:
                    finished = True
                else:
                    time.sleep(config.sample_interval)
                #endif

            #endwhile
        except virtualization.NoPingException, e:
            config = MonitorConfig.objects.get(domain=self.domain)
            config.flags |= MonitorConfig.FLAG_NO_PING
            config.save()
            transaction.commit()
            logging.error("%s: %s" % (self.domain.name, str(e)))
            raise       # re-raise
        #endtry

    #enddef

    def calculateCPUUsage(self, timeDiff, cpuTimeDiff):
        # 100 x cput_time_diff / (t x nr_cores x 10^9)
        percent = (100 * cpuTimeDiff) / (timeDiff * self.cores * 1000 * 1000 * 1000)

        # Because of errors our data can be not correct
        if percent > 100: percent = 100

        return percent
    #enddef

#endclass

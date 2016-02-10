# encoding=utf8

""" The probe framework
    Author: lipixun
    Created Time : 三  2/10 15:50:44 2016

    File Name: probe.py
    Description:

"""

import logging

PROBE_LOCATION_BEFORE_REQUEST   = 'beforeRequest'
PROBE_LOCATION_AFTER_REQUEST    = 'afterRequest'
PROBE_LOCATION_AFTER_RESPONSE   = 'afterResponse'

class ProbeFrame(object):
    """The probe frame which holds all probes and invoke the probes
    """
    logger = logging.getLogger('unifiedrpc.protocol.probe')

    def __init__(self, location2probes = None):
        """Create a new ProbeFrame
        """
        self.location2probes = location2probes or {}  # A dict which key is probe location, value is a list of probes

    def run(self, location):
        """Run the probe
        Parameters:
            location                    The probe location
        Returns:
            Nothing
        """
        probes = self.location2probes.get(location)
        if probes:
            for probe in probes:
                try:
                    probe()
                except:
                    self.logger.exception('Failed to invoke probe [%s] at location [%s]', probe, location)

    def add(self, location, method):
        """Add a probe method
        """
        if not location in self.location2probes:
            self.location2probes[location] = [ method ]
        elif not method in self.location2probes[location]:
            self.location2probes[location].append(method)


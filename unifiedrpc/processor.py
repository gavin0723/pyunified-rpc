# encoding=utf8

""" The whole dataflow processor from request to response
    Author: lipixun
    Created Time : 一  1/18 16:59:30 2016

    File Name: processor.py
    Description:

"""

from protocol import contextspace, context
from definition import *

class Processor(object):
    """A generic processor
    """
    def __init__(self, runtime, adapter):
        """Create the processor
        """
        self.runtime = runtime
        self.adapter = adapter

    def __call__(self):
        """Start the process
        """
        with contextspace(self.runtime, self.adapter):
            # Initialize the context
            self.initContext()


    def initContext(self):
        """Initialize the context
        """
        # The basic components for current context
        context.components.contentParser = self.contentParser
        context.components.contentBuilder = self.contentBuilder

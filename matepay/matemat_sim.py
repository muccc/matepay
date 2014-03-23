#!/usr/bin/python
import sys
import logging
from decimal import Decimal

class Matemat:
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        pass

    def writeLCD(self, msg):
        self._logger.info('writeLCD(): msg=%s' % msg)
    
    def getCost(self):
        print 'cost?'
        return Decimal(sys.stdin.readline().strip())

    def serve(self):
        return True

    def completeserve(self):
        return True


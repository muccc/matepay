#!/usr/bin/python

import sys
import logging

class Matemat:
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        pass

    def writeLCD(self, msg):
        self._logger.info('writeLCD(): msg=%s' % msg)
    
    def getPriceline(self):
        while True:
            try:
                print 'Priceline?'
                p = int(sys.stdin.readline().strip())
                self._logger.debug('priceline=%s' % p)
                return p
            except ValueError:
                pass

    def serve(self,priceline):
        self._logger.info('priceline=%s' % priceline)
        # always serve
        return True

    def completeserve(self):
        return True

# "Testing"
if __name__ == '__main__':
    m = MatematSim()
    m.writeLCD("luvv")
    while m.getPriceline() != 3:
        time.sleep(0.2)
    m.serve(3)
    m.completeserve()


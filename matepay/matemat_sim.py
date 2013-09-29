#!/usr/bin/python

import sys
from upay.logger import getLogger, flogger

class Matemat:
    log = getLogger('MatematSim')

    def __init__(self):
        pass

    @flogger(log)
    def writeLCD(self, msg):
        self.log.info('writeLCD(): msg=%s' % msg)
    
    @flogger(log)
    def getPriceline(self):
        while True:
            try:
                print 'Priceline?'
                p = int(sys.stdin.readline().strip())
                self.log.debug('priceline=%s' % p)
                return p
            except ValueError:
                pass

    @flogger(log)
    def serve(self,priceline):
        self.log.info('priceline=%s' % priceline)
        # always serve
        return True

    @flogger(log)
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


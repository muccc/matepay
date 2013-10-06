import time, sys
sys.path.insert(0, '.')

import serialinterface
from decimal import Decimal

class Matemat(object):
    def __init__(self):
        self.interface = serialinterface.SerialInterface('/dev/ttyUSB0',
                115200, timeout = 5)
        
        self.pricelines = {1: {'cost': Decimal("1.5")}, 3: {'cost': Decimal("1.0")}}

        self.interface.start()

    def getMessage(self):
        return self.interface.get_message()

    def _waitForReply(self,reply):
        #self.log.debug('reply=%s' % reply)
        print 'reply=%s' % reply
        while True:
            command, data = self.getMessage()
            print "read message", command, data
            if command == False:
                return False
            if data in reply:
                #self.log.debug('msg=%s' % msg)
                print 'data = %s' % data
                return data

    def writeLCD(self, msg):
        #self.log.info('writeLCD(): msg=%s' % msg)
        msg = "d"+msg
        self.interface.writeMessage('0', msg);
        return self._waitForReply(["dD"])
    
    def getCost(self):
        self.interface.writeMessage('0', "p")
        command, data = self.getMessage()

        if command == False:
            return -1

        if data[0] == 'p':
            priceline = int(data[2])
            self._last_priceline = priceline

            if priceline > 0:
                cost = self.pricelines[priceline]['cost']
                return cost
        return 0

    def serve(self):
        #self.log.info('priceline=%s' % priceline)
        self.interface.writeMessage('0', "s"+str(self._last_priceline))
        ret = self._waitForReply(["sO","sN"])
        if ret == False:
            return False
        if ret == "sN":
            return False
        return True

    def completeserve(self):
        return self._waitForReply(["sD"])

# "Testing"
if __name__ == '__main__':
    m = Matemat()
    m.start()
    m.writeLCD("luvv")
    time.sleep(10);
    while m.getCost() != Decimal("1.0"):
        time.sleep(0.2)
    m.serve()
    m.completeserve()


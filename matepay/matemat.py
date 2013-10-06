import serialinterface
from decimal import Decimal
import threading
import sys

class Matemat(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.interface = serialinterface.SerialInterface('/dev/ttyUSB0',
                115200, timeout = 5)
        
        self.pricelines = {1: {'cost': Decimal("1.5")}, 3: {'cost': Decimal("1.0")}}

        self.interface.create_channel('C')
        self.interface.create_channel('T')
        self.interface.start()
        self.start()

    def run(self):
        import re, pfu
        r = re.compile("temp([0-1])=([+,-][0-9]+\\.[0-9])")
        channels = ("temp", "mitte")

        while len(sys.argv) > 1:
            data = self.interface.get_message(channel = 'T', block = True, timeout = None)
            
            m = r.match(data)
            if m:
                channel = channels[int(m.groups()[0])]
                temperature = float(m.groups()[1])
                try:
                    feed = pfu.PachubeFeedUpdate("65835", sys.argv[1])
                    feed.addDatapoint(channel, temperature)
                    feed.buildUpdate()
                    feed.sendUpdate()
                except Exception as e:
                    print e

    def getMessage(self):
        return self.interface.get_message(channel = 'C', block = True, timeout = 5)

    def _waitForReply(self,reply):
        #self.log.debug('reply=%s' % reply)
        print 'reply=%s' % reply
        while True:
            data = self.getMessage()
            print "read message", data
            if data == False:
                return False
            if data in reply:
                #self.log.debug('msg=%s' % msg)
                print 'data = %s' % data
                return data

    def writeLCD(self, msg):
        #self.log.info('writeLCD(): msg=%s' % msg)
        msg = "d"+msg
        self.interface.writeMessage('C', msg);
        return self._waitForReply(["dD"])
    
    def getCost(self):
        self.interface.writeMessage('C', "p")
        data = self.getMessage()

        if data == False:
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
        self.interface.writeMessage('C', "s"+str(self._last_priceline))
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
    import time
    m = Matemat()
    m.start()
    m.writeLCD("luvv")
    time.sleep(10);
    while m.getCost() != Decimal("1.0"):
        time.sleep(0.2)
    m.serve()
    m.completeserve()


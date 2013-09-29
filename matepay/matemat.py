import time, sys
sys.path.insert(0, '.')

import serialinterface
import Queue, threading

class Matemat(threading.Thread):
    messages = Queue.Queue()

    def __init__(self):
        threading.Thread.__init__(self)
        self.interface = serialinterface.SerialInterface('/dev/ttyUSB0',
                115200, 5)
        self.setDaemon(True)

    def run(self):
        while 1:
            cmd, message = self.interface.readMessage()

            self.messages.put(message)

    def getMessage(self):
        return self.messages.get(block=True)

    def _waitForReply(self,reply):
        #self.log.debug('reply=%s' % reply)
        print 'reply=%s' % reply
        while True:
            msg = self.getMessage()
            print "read message", msg
            if msg == False:
                return False
            if msg in reply:
                #self.log.debug('msg=%s' % msg)
                print 'msg=%s' % msg
                return msg

    def writeLCD(self, msg):
        #self.log.info('writeLCD(): msg=%s' % msg)
        msg = "d"+msg
        self.interface.writeMessage('0', msg);
        return self._waitForReply(["dD"])
    
    def getPriceline(self):
        self.interface.writeMessage('0', "p")
        while True:
            msg = self.getMessage()
            if msg == False:
                return -1
            if msg[0] == 'p':
                #self.log.debug('priceline=%s' % msg[2])
                return int(msg[2])

    def serve(self,priceline):
        #self.log.info('priceline=%s' % priceline)
        self.interface.writeMessage('0', "s"+str(priceline))
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
    while m.getPriceline() != 1:
        time.sleep(0.2)
    m.serve(1)
    m.completeserve()


# $Id: checkout.py 84 2009-02-26 23:08:06Z fpletz $
# ----------------------------------------------------------------------------
# "THE MATE-WARE LICENSE"
# codec <codec@muc.ccc.de> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a mate in return.
# ----------------------------------------------------------------------------

import socket
import sys
import time
import threading
import nupay
import logging
from decimal import Decimal

class Matepay(threading.Thread):
    def __init__(self, testing = False):
        threading.Thread.__init__(self)
        self._logger = logging.getLogger(__name__)
        
        if not testing:
            import matemat as matemat
        else:
            import matemat_sim as matemat

        self.matemat = matemat.Matemat()
        self.matemat.start()
        self.token_reader = nupay.USBTokenReader()
        while 1:
            try:
                self.matemat.writeLCD('connecting...')
                self.session_manager = nupay.SessionManager()
                break;
            except nupay.SessionConnectionError as e:
                self.report("upay unavailable", wait=3)

        self.pricelines = {1: {'cost': Decimal("1")}, 3: {'cost': Decimal("1.5")}}
 
    def go(self):
        self.matemat.writeLCD('OBEY AND CONSUME')
        
        print("Waiting for purse")
        
        while True: 
            try:
                tokens = self.token_reader.read_tokens()
                break
            except nupay.NoTokensAvailableError:
                time.sleep(1)

        print("Read %d tokens" % len(tokens))
       
        with self.session_manager.create_session() as session:
            session.validate_tokens(tokens)
            
            self._logger.debug('credit=%.02f Eur' % session.credit)
            self.report('Credit: %.02f Eur' % session.credit)

            while self.token_reader.medium_valid:
                priceline = self.matemat.getPriceline()
                if priceline == -1:
                    self.report('TIMEOUT', 3)
                    return
                elif priceline != 0:
                    self._logger.info('priceline=%s' % priceline)
                    break
                time.sleep(0.01)
            
            if not self.token_reader.medium_valid:
                self.report('Next time ;)', 3)
                return
            try: 
                transaction = session.cash(self.pricelines[priceline]['cost'])

                if self.matemat.serve(priceline):
                    self._logger.info('Serving %s' % priceline)
                    self.report('%.02f Eur left' % session.credit, 3)
                else:
                    self._logger.info('Failed to serve %s' % priceline)
                    self.report('Failed to serve!', 3)
                    session.rollback(transaction)
                    return

                if False: #not self.matemat.completeserve():
                    self._logger.info('Failed to complete serve %s' % priceline)
                    self.report('Failed to cserve!', 3)
                    self.token.rollback(priceline)
            except nupay.NotEnoughCreditError as e:
                self.report('%.02f Eur missing' % e[0][1], 3)
                return

        #print("Waiting for medium to vanish")
        #while self.token_reader.medium_valid:
        #    time.sleep(.5)

    def report(self, msg, wait=0):
        self.matemat.writeLCD(msg)
        if wait != 0:
            time.sleep(wait)
    
#self.report('ERR: Bad Purse!', 3)
#self.report('ERR: %s' % data[:15], 3)
#self.report('Credit: %s' % self.token.tokencount)

    def run(self):
        while 1:
            try:
                self.go()
            except nupay.SessionConnectionError as e:
                self.report('upay unavailable', 3)
            except nupay.SessionError as e:
                self.report('upay terminated', 3)
            except Exception as e:
                self._logger.warning("unhandled exception", exc_info=True)

# "Testing"
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    co = Matepay()
    co.start()
    co.join()


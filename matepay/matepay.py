# $Id: checkout.py 84 2009-02-26 23:08:06Z fpletz $
# ----------------------------------------------------------------------------
# "THE MATE-WARE LICENSE"
# codec <codec@muc.ccc.de> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a mate in return.
# ----------------------------------------------------------------------------

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
        self.token_reader = nupay.USBTokenReader()

        while True:
            try:
                self.matemat.writeLCD('connecting...')
                self.session_manager = nupay.SessionManager()
                break;
            except nupay.SessionConnectionError as e:
                self.report("upay unavailable", wait = 3)

    def go(self):
        self.matemat.writeLCD('OBEY AND CONSUME')
        
        self._logger.debug("Waiting for purse")
        
        while True: 
            try:
                tokens = self.token_reader.read_tokens()
                break
            except nupay.NoTokensAvailableError:
                time.sleep(1)

        self._logger.debug("Read %d tokens" % len(tokens))
       
        with self.session_manager.create_session() as session:
            session.validate_tokens(tokens)
            
            self._logger.debug('credit=%.02f Eur' % session.credit)
            self.report('Credit: %.02f Eur' % session.credit)

            while self.token_reader.medium_valid:
                cost = self.matemat.getCost()
                if cost == -1:
                    self.report('TIMEOUT', wait = 3)
                    return
                elif cost != 0:
                    self._logger.info('cost=%s' % cost)
                    break
                time.sleep(0.1)
            else: 
                self.report('Next time ;)', wait = 3)
                return

            try: 
                transaction = session.cash(cost)

                if self.matemat.serve():
                    self._logger.info('Serving')
                    self.report('%.02f Eur left' % session.credit, wait = 3)
                else:
                    self._logger.info('Failed to serve')
                    self.report('Failed to serve!', 3)
                    session.rollback(transaction)

                if False: #not self.matemat.completeserve():
                    self._logger.info('Failed to complete serve')
                    self.report('Failed to cserve!', 3)
                    session.rollback(cost)

            except nupay.NotEnoughCreditError as e:
                self.report('%.02f Eur missing' % e[0][1], wait = 3)
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

    def serve(self):
        while True:
            try:
                self.go()
            except nupay.SessionConnectionError as e:
                self.report('upay unavailable', wait = 3)
            except nupay.SessionError as e:
                self.report('upay terminated', wait = 3)
            except Exception as e:
                self.report('see error log', wait = 3)
                self._logger.warning("unhandled exception", exc_info=True)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    matepay = Matepay()
    matepay.serve()


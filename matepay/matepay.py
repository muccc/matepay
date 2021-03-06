# $Id: checkout.py 84 2009-02-26 23:08:06Z fpletz $
# ----------------------------------------------------------------------------
# "THE MATE-WARE LICENSE"
# codec <codec@muc.ccc.de> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a mate in return.
# ----------------------------------------------------------------------------

import time
import threading
import upay.client
import upay.common
import logging
import sys

from decimal import Decimal
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

testing = True

if not testing:
    import matemat as matemat
else:
    import matemat_sim as matemat


class Matepay(threading.Thread):
    def __init__(self, cipher):
        threading.Thread.__init__(self)
        self._logger = logging.getLogger(__name__)
        self.matemat = matemat.Matemat()
        self.token_reader = upay.common.USBTokenReader()
        self._collector = upay.common.MQTTCollector(cipher = cipher, server = 'localhost', topic = '/collected/matmat', client_id = 'matemat')

        while True:
            try:
                self.matemat.writeLCD('connecting...')
                self.session_manager = upay.client.SessionManager(collectors = [self._collector])
                break
            except upay.client.SessionConnectionError as e:
                self.report("upay unavailable", wait = 3)

    def go(self):
        self.matemat.writeLCD('OBEY AND CONSUME')
        
        while not self._collector.connected:
            self.report('upay unavailable', wait = 3)

        self._logger.debug("Waiting for purse")

        while True: 
            try:
                tokens = self.token_reader.read_tokens()
                break
            except upay.common.NoTokensAvailableError:
                time.sleep(1)

        self._logger.debug("Read %d tokens" % len(tokens))
       
        with self.session_manager.create_session() as session:
            session.validate_tokens(tokens)
            
            msg = 'Credit: %.02f Eur' % (session.credit)
            self._logger.debug(msg)
            self.report(msg)

            while self.token_reader.medium_valid:
                cost = self.matemat.getCost()
                if cost == -1:
                    self.report('TIMEOUT', wait = 3)
                    return
                elif cost != 0:
                    self._logger.info('cost=%.02f' % cost)
                    break
                time.sleep(0.1)
            else: 
                self.report('Next time ;)', wait = 3)
                return

            try: 
                assert(self._collector.connected)
                session.cash(cost)
                self.matemat.serve()
                session.collect()
                self._logger.info('Serving')
                msg = '%.02f Eur left' % (session.credit)
                self._logger.debug(msg)
                self.report(msg, wait = 3)

                if False: #not self.matemat.completeserve():
                    self._logger.info('Failed to complete serve')
                    self.report('Failed to cserve!', wait = 3)
                    session.rollback()

            except upay.client.NotEnoughCreditError as e:
                self.report('%.02f Eur missing' % e[0][1], wait = 3)
            except matemat.ServeError:
                self._logger.info('Failed to serve')
                self.report('Failed to serve!', wait = 3)
                session.rollback()

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
            except upay.client.SessionConnectionError as e:
                self.report('upay unavailable', wait = 3)
            except upay.client.SessionError as e:
                self.report('upay terminated', wait = 3)
            except Exception as e:
                self.report('see error log', wait = 3)
                self._logger.warning("unhandled exception", exc_info=True)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    key_file = open(sys.argv[1],'r')
    key = RSA.importKey(key_file.read())
    cipher = PKCS1_OAEP.new(key)
    matepay = Matepay(cipher = cipher)
    matepay.serve()


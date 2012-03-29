#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import socket
import threading
import datetime
import logging
from common import hash_file, CHUNKSIZE
from log import logger

class RozeClient(object):
    """docstring for RozeClient"""

    def __init__(self, server):
        self.server = server
        #threading.Thread.__init__(self)

    def run(self):
        self.s = socket.socket()
        self.s.connect(('localhost', 9191))
        self.logger = logging.getLogger('Client')
        self.logger.setLevel(logging.INFO)

    def stop(self):
        pass
    
    """def close(self):
        try:
            self._Thread__stop()
        except:
            print("%s could not be terminated" % self.getName())
    """

    def get_file(self, fn):
        cmd = 'GET\n%s' % (fn)
        self.s.sendall(cmd)

        # TODO: Save data to a file IN chunks.
        # Now "data" is held in memory,
        # causing serious issues.
        data = self._receive_file(fn)

        return data

    def _receive_file(self, fn):

        # Receive ack
        ack = self.s.recv(2)
        size = int(self.s.recv(16))
        buf = ''

        while size > len(buf):
            data = self.s.recv(CHUNKSIZE)
            if not data: 
                break
            buf += data
        self.s.sendall('Ok')

        return buf

        
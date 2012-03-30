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
        cmd = u'GET\nmybox/%s' % fn
        print "Fetching %s" % fn
        s.sendall(cmd.encode("utf-8"))
        ack = self.s.recv(2)
        print ack
        size = int(self.s.recv(16))
        print "Filesize: %s" % size 
        recvd = ''
        tmpfile = open(u'mybox/%s' % fn, 'wb')
        while size > len(recvd):
            print "DLed: %s" % len(recvd)
            data = self.s.recv(4096)
            if not data:
                break
            tmpfile.write(data)
            recvd += data
        tmpfile.close()
        self.s.sendall('ok')
        return recvd


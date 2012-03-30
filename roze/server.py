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
from indexer import RozeIndexer

class RozeServer(object): #threading.Thread):
    """ Main server class for receiving and sending files. Probably
    needs some fancy way to handle a pool of client connections through
    acl.
    This class should handle the following actions in future:

        - GET /path/to/file\n
        - PUT /path/to/file\nDATA\n
        - DELETE /path/to/file\n

    """

    def __init__(self, host, port):
        #super(RozeServer, self).__init__()
        self.host = host
        self.port = port
        self.logger = logging.getLogger('Server')
        self.logger.setLevel(logging.INFO)
        
        self.logger.info("Initializing indexer")
        self.indexer = RozeIndexer('mybox/') 

        #threading.Thread.__init__(self)

    def run(self):
        self.logger.info("Starting")
        self._start()

    def stop(self):
        self._Thread__stop()

    def _send_file(self, fn):

        with open(fn, 'rb') as f:
            data = f.read()
        if self._send_data(data):
            self.logger.info("\"%s\" sent!" % fn)


    def _ack(self, ackstr="Ok"):
        # Send ack
        self.s.sendall(ackstr)


    def _send_data(self, data):
        # Acknowledgement
        self._ack()
        
        # Send size as signed 16–bytes integer.
        self.s.sendall('%16d' % len(data))
        
        # Send the data.
        self.s.sendall(data)

        # Message sent succesfully?
        ack = self.s.recv(2)

        if ack.lower() == 'ok':
            return True
        else:
            return False
        

    def _main(self):

        while True:
            # Socket & address bound to the socket on the other end of the connection.
            self.s, a = self.c.accept()
            self.s.settimeout(35)
            while True:
                # For best match with hardware and network realities
                # the value of chunk/buffer size should be and a
                # relatively small power of 2.
                try:
                    data = self.s.recv(CHUNKSIZE).rstrip(os.linesep)
                except socket.timeout:
                    self.logger.info("Timeout detected")
                    # Close the client connection
                    self.s.close()
                    break

                # Returns the string after the first occurence of "\n"
                if data.find('\n') > 0:
                    cmd = data[:data.find('\n')]
                else:
                    cmd = data
                self.logger.info("Got command: '%s'\n" % cmd)

                if cmd == 'GET':
                    # Command & Filename
                    cmd, fn = data.split('\n', 2)
                    self._send_file(fn)

                if cmd == 'CLOSE':
                    # Close socket
                    self.s.close()
                    break

                if cmd == 'LIST':
                    file_listing = self.indexer.file_listing()
                    self.indexer.index()
                    self._send_data(file_listing)



    def _start(self):

        # IPv4 Address family & standard socket stream.
        self.c = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        # Fixes bug “Address already in use” -after socket has died/been killed.
        self.c.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind to all available interfaces.
        # Selected an arbitrary non-privileged port.
        self.c.bind(('0.0.0.0', 9191))

        # Accept only one client.
        self.c.listen(5)

        
        self._main()


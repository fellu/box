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

class RozeServer(threading.Thread):
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
        threading.Thread.__init__(self)


    def run(self):
        self.logger.info("Starting")
        self._start()

    def stop(self):
        self._Thread__stop()

    def _datasend(self, fn):
        # Send ack
        self.s.sendall('Ok')
        
        with open(fn, 'rb') as f:
            data = f.read()
        
        # Send size as signed 16–bytes integer.
        self.s.sendall('%16d' % len(data))
        
        # Send the data.
        self.s.sendall(data)

        # Message sent succesfully?
        ack = self.s.recv(2)

        if ack.lower() == 'ok':
            self.logger.info("File \"%s\" sent succesfully!" % fn)

    def _main(self):
        
        while True:
            # For best match with hardware and network realities
            # the value of chunk/buffer size should be and a
            # relatively small power of 2.
            data = self.s.recv(CHUNKSIZE)

            # Returns the string after the first occurence of "\n"
            cmd = data[:data.find('\n')]
            self.logger.info("Got command: '%s'" % cmd)

            if cmd == 'GET':
                cmd, fn = data.split('\n', 2)
                self._datasend(fn)

            if cmd == 'CLOSE' or cmd == '':
                # Close socket
                self.s.close()
                # Close connection
                self.c.close()
                break
            if cmd == '':
                self.s.sendall("Server did not understand you.")
                # Close socket
                self.s.close()
                # Close connection
                self.c.close()
                break

    def _start(self):

        # IPv4 Address family & standard socket stream.
        self.c = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        # Bind to all available interfaces.
        # Selected an arbitrary non-privileged port.
        self.c.bind(('0.0.0.0', 9191))

        # Accept only one client.
        self.c.listen(1)

        # Socket & address bound to the socket on the other end of the connection.
        self.s, a = self.c.accept()
        self._main()


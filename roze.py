#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "incidence <incidence@iki.fi>"
__copyright__ = "Copyright 2012, incidence"
__credits__ = ["incidence"]
__license__ = "GPL"
__version__ = "0.1.1"
__maintainer__ = "incidence"
__email__ = "incidence@iki.fi"
__status__ = "Unstable"

import os
import sys
import socket
import threading
import datetime
import logging
from common import hash_file, CHUNKSIZE
from roze import *
from roze.log import logger

class Roze(object):
    def __init__(self, host, port, box_path):
        self.logger = logging.getLogger('Main')
        self.logger.setLevel(logging.INFO)

        self.box_path = box_path
        
        self.logger.info("Initializing server")
        self.server = RozeServer(host, port)
        
        self.logger.info("Starting server")
        self.server.start()

        self.logger.info("Initializing client")
        self.client = RozeClient('127.0.0.1')
        self.client.run()
        
        self.logger.info("Initializing indexer")
        self.indexer = RozeIndexer(box_path) 

    def kill(self):
        self.server.stop()
        self.client.stop()
        del self.server
        del self.client
        sys.exit(0)

def main():
    try:
        # Just to test the scripts.
        R = Roze('localhost', 9191, 'mybox/')
        # Run the indexer.
        R.indexer.index()
    except KeyboardInterrupt:
        R.kill()


if __name__ == '__main__':
    main()
    
    
    
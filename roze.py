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
from common import hash_file, CHUNKSIZE

class RozeServer(object):
    """ Main server class for receiving and sending files. Probably
    needs some fancy way to handle a pool of client connections through
    acl.
    This class should handle the following actions in future:

        - GET /path/to/file\n
        - PUT /path/to/file\nDATA\n
        - DELETE /path/to/file\n

    """

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.start()

    def start(self):

        # IPv4 Address family & standard socket stream.
        self.c = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        # Bind to all available interfaces.
        # Selected an arbitrary non-privileged port.
        self.c.bind(('0.0.0.0', 9191))

        # Accept only one client.
        self.c.listen(1)

        # Socket & address bound to the socket on the other end of the connection.
        self.s, a = self.c.accept()
        self._main_loop()


    def send(self, fn):
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
            print "File \"%s\" sent succesfully!" % fn
    

    def get_file(self, fn):
        cmd = 'GET\n%s' % (fn)
        self.s.sendall(cmd)

        # TODO: Save data to a file IN chunks.
        # Now "data" is held in memory,
        # causing serious issues.
        data = self._receive_file(fn)


    def _main_loop(self):
        while True:
            # For best match with hardware and network realities
            # the value of chunk/buffer size should be and a
            # relatively small power of 2.
            data = self.s.recv(CHUNKSIZE)

            # Returns the string after the first occurence of "\n"
            cmd = data[:data.find('\n')]
            print "Got command: '%s'" % cmd

            if cmd == 'GET':
                cmd, fn = data.split('\n', 2)
                self.send(fn)

            if cmd == 'CLOSE':
                # Close socket
                self.s.close()
                # Close connection
                self.c.close()
                break


    def _receive_file(self):

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


class RozeIndexer(object):
    
    def __init__(self, box_path):
        self.box_path = os.path.join(box_path)
        self.registry = os.path.join(box_path, '.meta/')
        
        if not os.path.isdir(self.registry):
            os.makedirs(self.registry)

    def index(self):
        current_blobs = []

        for infile in os.listdir(self.box_path):
            if os.path.isdir(infile) or infile == '.meta':
                continue

            # Get file full path
            full_path = os.path.join(self.box_path, infile)
            checksum = hash_file(full_path)

            # Just to ease debugging.
            data = '%s:%s\n' % (checksum, infile,)

            blobpath = os.path.join(self.registry, checksum)

            # Append to current blobs
            current_blobs.append({
                'checksum': checksum,
                'filename': blobpath
            })

            # Write the blob if we don't already have it.
            if not os.path.isfile(blobpath):
                try:
                    # Todo, write much more information to the meta-blob file.
                    # Last modified, which server modified, ..
                    print("Writing blob %s (%s)" % (checksum, infile,))
                    blobfile = open(blobpath, 'w')
                    blobfile.write(data)
                    blobfile.close()
                except IOError:
                    raise Exception("Writing a blob failed")
            else:
                print("Blob %s exists" % checksum)

        # Clear orphaned files.
        for checksum in os.listdir(self.registry):
            blob_path = os.path.join(self.registry, checksum)
            content = open(blob_path, 'r').read()
            found = False

            for current in current_blobs:
                if current['checksum'] == checksum:
                    found = True
                    break
            if not found:
                print "Found obsolete %s blob" % checksum
                os.unlink(blob_path)


    def sync(self):
        raise NotImplementedError


class Roze(object):
    def __init__(self, host, port, box_path):
        self.box_path = box_path
        self.server = RozeServer(host, port)    
        self.indexer = RozeIndexer(box_path) 


def main():
    # Just to test the scripts.
    R = Roze('localhost', 9191, 'mybox/')
    # Run the indexer.
    R.indexer.index()


if __name__ == '__main__':
    main()
    
    
    
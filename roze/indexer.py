#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import socket
import threading
import datetime
try: import simplejson as json
except ImportError: import json
from common import hash_file, CHUNKSIZE

class RozeIndexer(object):
    """ Indexer process, which should request changed files in sync
    from the server process."""

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

    def file_listing(self, recursive=False):
        listing = []

        for infile in os.listdir(self.box_path):
            # Todo: recursive listing?
            if os.path.isdir(infile) or infile == '.meta':
                continue
            listing.append(infile)
        return json.dumps(listing)

    def sync(self):
        raise NotImplementedError



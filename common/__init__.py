#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime
from hashlib import sha1

CHUNKSIZE = 4096

def get_file_timetamp(data):
    return os.path.getmtime(data)


def get_file_size(data):
    return str(os.path.getsize(data))


def hash_file(data):

    size = str(os.path.getsize(data))
    basename = os.path.basename(data)

    f = open(data, 'r')

    s = sha1()
    s.update("blob %s%s\0" % (size, basename,))

    file = open(data, "rb")
    try:
        bytes_read = file.read(CHUNKSIZE)
        while bytes_read:
            for b in bytes_read:
                s.update(b)
            bytes_read = file.read(CHUNKSIZE)
    finally:
        file.close()

    return s.hexdigest()

# "These aren't the chunks you're looking for" or some other SW quote.
class WrongChunkError(Exception): pass

# If chunk wasn't received properly.
class NotReceivedError(Exception): pass

# Should be raised when the requested file was not found.
class FileNotFoundError(Exception): pass

# Should be raised if a client doesn't have proper permission
# to access host's files.
class RestrictedAccessError(Exception): pass

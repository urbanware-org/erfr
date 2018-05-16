#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# ============================================================================
# Erfr - One-time pad encryption tool
# Obfuscator core module
# Copyright (C) 2018 by Ralf Kilian
# Distributed under the MIT License (https://opensource.org/licenses/MIT)
#
# Website: http://www.urbanware.org
# GitHub: https://github.com/urbanware-org/erfr
# ============================================================================

__version__ = "4.3.3"

import common
import os
import paval as pv
import randgen
import time

def add_random_bytes(file_path, buffer_size=4096, bytes_random=0,
                     dev_random=False, fortuna=False):
    """
        Add given amount of random bytes to a file.
    """
    delay = common.get_delay()

    pv.path(file_path, "target", True, True)
    pv.intvalue(buffer_size, "buffer size", True, False, False)
    pv.intvalue(bytes_random, "random bytes", True, False, False)

    buffer_size = int(buffer_size)
    bytes_random = int(bytes_random)
    file_path = os.path.abspath(file_path)

    byte_blocks = int(bytes_random / buffer_size)
    byte_remainder = bytes_random % buffer_size
    data_random = bytearray(b"")

    always_use_urandom = \
        bool(int(common.global_config(["Obfuscator"], ["always_use_urandom"],
                                      dev_random)))

    if always_use_urandom:
        dev_random = False

    prng = randgen.get_prng(dev_random, fortuna)
    fh_target = open(file_path, "ab")

    for block in range(byte_blocks):
        data_random = prng.get_bytes(buffer_size)
        fh_target.write(data_random)
        time.sleep(delay)

    if byte_remainder > 0:
        data_random = prng.get_bytes(byte_remainder)
        fh_target.write(data_random)
        time.sleep(delay)

    fh_target.close()

def get_version():
    """
        Return the version of this module.
    """
    return __version__

def obfuscate_file(task_id, file_path, buffer_size=4096, bytes_random=0,
                   dev_random=False, fortuna=False):
    """
        Create a task file first, then add given amount of random bytes
        to the given file.
    """
    pv.path(file_path, "target", True, True)
    pv.intvalue(buffer_size, "buffer size", True, False, False)
    pv.intvalue(bytes_random, "random bytes", True, False, False)

    buffer_size = int(buffer_size)
    bytes_random = int(bytes_random)
    file_path = os.path.abspath(file_path)
    file_size = common.get_file_size(file_path) + int(bytes_random)

    common.build_task_file(task_id, file_path, file_size, None, 0, None, 0,
                          "file obfuscation")

    add_random_bytes(file_path, buffer_size, bytes_random, dev_random,
                     fortuna)

# EOF

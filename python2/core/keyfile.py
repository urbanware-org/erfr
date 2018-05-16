#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# ============================================================================
# Erfr - One-time pad encryption tool
# Key file core module
# Copyright (C) 2018 by Ralf Kilian
# Distributed under the MIT License (https://opensource.org/licenses/MIT)
#
# Website: http://www.urbanware.org
# GitHub: https://github.com/urbanware-org/erfr
# ============================================================================

__version__ = "4.3.3"

import base64
import common
import obfuscator
import os
import paval as pv
import randgen
import sys
import tempfile
import time

def base64_key(task_id, base64_string):
    """
        Convert a Base64 key string into a temporary key file.
    """
    if task_id == None:
        common.exception("A task ID is required to convert a Base64 string " \
                        "into a temporary key file.")

    base64_string = str(base64_string)
    if base64_string == "":
        common.exception("The Base64 string must not be empty.")

    try:
        data_key = bytearray(b"" + base64.b64decode(base64_string))
    except ValueError:
        common.exception("The given Base64 key string contains invalid " \
                        "characters.")
    except:
        common.exception("The given Base64 key string is not valid.")

    file_key = os.path.join(tempfile.gettempdir(), "erfr_" +
                            str(task_id).rjust(4, "0") + ".key")
    fh_key = open(file_key, "wb")
    fh_key.write(data_key)
    fh_key.close()

    return file_key

def build_file_key(file_path, file_size, buffer_size=4096, bytes_random=0,
                   use_existing_key=False, dev_random=False, fortuna=False,
                   overwrite=False, parts=1):
    """
        Build a key file which contains the random values which are required
        to encrypt the input file.
    """
    delay = common.get_delay()

    if use_existing_key:
        pv.path(file_path, "key", True, True)
    else:
        if not overwrite:
            pv.path(file_path, "key", True, False)
            pv.path(file_path + ".001", "key part", True, False)
    file_path = os.path.abspath(file_path)

    pv.intvalue(file_size, "key file size", True, False, False)
    pv.intvalue(buffer_size, "buffer size", True, False, False)
    pv.intvalue(bytes_random, "random bytes", True, True, False)
    pv.intvalue(parts, "key file parts", True, False, False)

    file_size = int(file_size)
    buffer_size = int(buffer_size)
    bytes_random = int(bytes_random)
    parts = int(parts)

    if parts > (file_size + bytes_random):
        common.exception("The file is too small for given number of key " \
                         "parts.")
    elif parts > 999:
        common.exception("The number of key parts must be less than 1000.")

    if not use_existing_key:
        key_path = file_path
        part_id = 0
        part_temp = int(file_size + bytes_random)
        part_size = part_temp / parts
        part_last = part_temp - (part_size * (parts - 1))
        for part in range(parts):
            if parts > 1:
                part_id += 1
                key_path = file_path + "." + str(part_id).rjust(3, "0")
                if part_id < parts:
                    file_size = part_size
                else:
                    file_size = part_last

            data_key = bytearray(b"")
            fh_key = open(key_path, "wb")
            byte_blocks = int(file_size / buffer_size)
            byte_remainder = file_size % buffer_size

            prng = randgen.get_prng(dev_random, fortuna)
            for block in range(byte_blocks):
                data_key = prng.get_bytes(buffer_size)
                fh_key.write(data_key)
                time.sleep(delay)

            if byte_remainder > 0:
                data_key = prng.get_bytes(byte_remainder)
                fh_key.write(data_key)
                time.sleep(delay)

            fh_key.close()

    if parts == 1:
        if bytes_random > 0:
            obfuscator.add_random_bytes(file_path, buffer_size, bytes_random,
                                        dev_random)

def compare_files(file_input, directory, ignore_read_errors=True,
                  obfuscate_enc=0, obfuscate_key=0):
    """
        Compare files to find out which key fits to an encrypted file
        and vice versa.
    """
    pv.path(file_input, "input", True, True)
    pv.path(directory, "compare", False, True)
    pv.intvalue(obfuscate_enc, "encrypted file obfuscation", True, True, \
                False)
    pv.intvalue(obfuscate_key, "key file obfuscation", True, True, False)

    obfuscate_enc = int(obfuscate_enc)
    obfuscate_key = int(obfuscate_key)

    file_input = os.path.abspath(file_input)
    file_input_size = int(common.get_file_size(file_input))

    directory = os.path.abspath(directory)
    list_files = []

    for item in os.listdir(directory):
        path = os.path.join(directory, item)
        if os.path.isfile(path):
            if path == file_input:
                continue

            file_enc_size1 = int(common.get_file_size(path) + obfuscate_enc)
            file_enc_size2 = int(common.get_file_size(path) - obfuscate_enc)
            file_key_size1 = int(common.get_file_size(path) + obfuscate_key)
            file_key_size2 = int(common.get_file_size(path) - obfuscate_key)

            try:
                if file_input_size == file_enc_size1 or \
                   file_input_size == file_enc_size2 or \
                   file_input_size == file_key_size1 or \
                   file_input_size == file_key_size2:
                    list_files.append(path)
            except Exception as e:
                if not ignore_read_errors:
                    raise Exception(e)
                else:
                    pass

    list_files.sort()

    return list_files

def merge_key(file_output, buffer_size=4096, overwrite=False):
    """
        Merge multiple key file parts to a single key file.
    """
    if not overwrite:
         pv.path(file_output, "output key", True, False)
    else:
        pv.path(file_output, "key", True, True)

    part_id = 0
    fh_output = open(file_output, "wb")
    while True:
        part_id += 1
        file_key = file_output + "." + str(part_id).rjust(3, "0")
        if not os.path.exists(file_key):
            break

        fh_key = open(file_key, "rb")
        file_size = common.get_file_size(file_key)
        byte_blocks = int(file_size / buffer_size)
        byte_remainder = file_size % buffer_size

        for block in range(byte_blocks):
            fh_output.write(fh_key.read(buffer_size))

        if byte_remainder > 0:
            fh_output.write(fh_key.read(byte_remainder))

        fh_key.close()

    fh_output.close()

def generate_key_file(task_id, file_path, file_size, buffer_size=4096,
                      bytes_random=0, use_existing_key=False,
                      dev_random=False, fortuna=False, overwrite=False,
                      parts=1):
    """
        Create a task file first, then build the key file.
    """
    if use_existing_key:
        pv.path(file_path, "key", True, True)
    else:
        if not overwrite:
            pv.path(file_path, "key", True, False)

    pv.intvalue(file_size, "key file size", True, False, False)
    pv.intvalue(buffer_size, "buffer size", True, False, False)
    pv.intvalue(bytes_random, "random bytes", True, True, False)
    pv.intvalue(parts, "key file parts", True, False, False)

    file_path = os.path.abspath(file_path)
    file_size = int(file_size)
    buffer_size = int(buffer_size)
    bytes_random = int(bytes_random)

    if parts == 1:
        generation_type = "key generation"
    else:
        generation_type = "multi-part key generation"

    file_size = file_size + bytes_random

    common.build_task_file(task_id, file_path, file_size, None, 0, None, 0,
                           generation_type)


    build_file_key(file_path, file_size, buffer_size, bytes_random, False,
                   dev_random, fortuna, overwrite, parts)

def generate_key_string(key_bytes, dev_random=False, fortuna=False):
    """
        Generate a binary key and convert it into a Base64 string.
    """
    pv.intvalue(key_bytes, "key size", True, False, False)
    key_bytes = int(key_bytes)

    prng = randgen.get_prng(dev_random, fortuna)
    key_string = prng.get_bytes(key_bytes)

    # Run the appropriate code for the Python framework used
    if sys.version_info[0] == 2:
        key_string = base64.b64encode(key_string)
    elif sys.version_info[0] > 2:
        key_bytes = base64.b64encode(key_string)
        key_string = key_bytes.decode(sys.getdefaultencoding())

    return key_string

def get_version():
    """
        Return the version of this module.
    """
    return __version__

def split_key(file_input, parts, buffer_size=4096, overwrite=False):
    """
        Split a key file in a user-defined number of parts.
    """
    if not overwrite:
         pv.path(file_input, "key", True, True)
         pv.path(file_input + ".001", "key part", True, False)
    else:
        pv.path(file_input, "key", True, True)

    buffer_size = int(buffer_size)
    parts = int(parts)

    if parts < 2:
        common.exception("The number of key parts must be greater than 1.")
    elif parts > 999:
        common.exception("The number of key parts must be less than 1000.")

    file_size = common.get_file_size(file_input)
    part_id = 0
    part_size = int(file_size / parts)
    part_last = file_size - (part_size * (parts - 1))

    fh_input = open(file_input, "rb")
    for part in range(parts):
        part_id += 1
        file_key = file_input + "." + str(part_id).rjust(3, "0")
        if part_id < parts:
            file_size = int(part_size)
        else:
            file_size = int(part_last)

        fh_output = open(file_key, "wb")

        byte_blocks = int(file_size / buffer_size)
        byte_remainder = file_size % buffer_size

        for block in range(byte_blocks):
            fh_output.write(fh_input.read(buffer_size))

        if byte_remainder > 0:
            fh_output.write(fh_input.read(byte_remainder))

        fh_output.close()

    fh_input.close()

# EOF

#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# ============================================================================
# Erfr - One-time pad encryption tool
# Main encryption/decryption core module
# Copyright (C) 2018 by Ralf Kilian
# Distributed under the MIT License (https://opensource.org/licenses/MIT)
#
# Website: http://www.urbanware.org
# GitHub: https://github.com/urbanware-org/erfr
# ============================================================================

__version__ = "4.3.3"

import common
import keyfile
import obfuscator
import os
import parameter
import paval as pv
import rotate as rt
import sbox
import time

def get_version():
    """
        Return the version of this module.
    """
    return __version__

class ErfrCrypt(object):
    """
        Class for Erfr encryption/decryption.
    """
    __task_id = None
    __encrypt = True

    __file_input = None
    __file_key = None
    __file_output = None
    __file_size = 0
    __file_export = None

    __buffer_size = 4096
    __existing_key = False
    __overwrite = False

    __obfuscate_enc = 0
    __obfuscate_key = 0

    __fortuna = False
    __dev_random = False

    __rotate = False
    __rotate_min = 0
    __rotate_max = 0
    __rotate_step = 0
    __rotate_mod = False
    __rotate_obj = None

    __reverse = False
    __reverse_bytes = 0

    __sbox = False

    def __init__(self):
        return

    def decrypt_file(self, task_id, file_input, file_key, file_output,
                     buffer_size, overwrite=False, obfuscate_enc=0,
                     obfuscate_key=0, rotate_min=0, rotate_max=0,
                     rotate_step=0, rotate_mod=False, reverse_bytes=0,
                     sbox=False):
        """
            Decrypt a file with the given options.
        """
        self.__encrypt = False
        self.__prepare_process(task_id, file_input, file_key, file_output,
                               buffer_size, False, overwrite, obfuscate_enc,
                               obfuscate_key, None, None, rotate_min,
                               rotate_max, rotate_step, rotate_mod,
                               reverse_bytes, sbox, False)
        self.__decrypt_file()
        self.__reset()

    def encrypt_file(self, task_id, file_input, file_key, file_output,
                     buffer_size, existing_key=False, overwrite=False,
                     obfuscate_enc=0, obfuscate_key=0, fortuna=False,
                     dev_random=False, rotate_min=0, rotate_max=0,
                     rotate_step=0, rotate_mod=False, reverse_bytes=0,
                     sbox=False, export_file=None):
        """
            Encrypt a file with the given options.
        """
        self.__encrypt = True

        export = False
        skip_checks = False

        if not export_file == None:
            export = True
            skip_checks = bool( \
                int(common.global_config(["Export"], ["skip_checks"], "0")))

        self.__prepare_process(task_id, file_input, file_key, file_output,
                               buffer_size, existing_key, overwrite,
                               obfuscate_enc, obfuscate_key, fortuna,
                               dev_random, rotate_min, rotate_max,
                               rotate_step, rotate_mod, reverse_bytes, sbox,
                               skip_checks)

        if export:
            self.__file_export = export_file
            self.__export(overwrite)
        else:
            self.__encrypt_file()
        self.__reset()

    def __decrypt_file(self):
        """
            Core method to decrypt a file.
        """
        fs_input = common.get_file_size(self.__file_input)
        fs_key = common.get_file_size(self.__file_key)
        fs_output = fs_input - self.__obfuscate_enc

        if self.__reverse_bytes > fs_input:
            common.exception("The reverse byte value must not be greater " \
                             "than the input file size.")

        common.build_task_file(self.__task_id, self.__file_input, fs_input,
                               self.__file_key, fs_key, self.__file_output,
                               fs_output, "decryption")

        self.__file_size = fs_output
        self.__erfr_core()

    def __encrypt_file(self):
        """
            Core method to encrypt a file.
        """
        fs_input = common.get_file_size(self.__file_input)
        fs_output = fs_input + self.__obfuscate_enc

        if self.__reverse_bytes > fs_input:
            common.exception("The reverse byte value must not be greater " \
                             "than the input file size.")

        if self.__existing_key:
            fs_key = common.get_file_size(self.__file_key)
            if (fs_key - self.__obfuscate_key) < \
               (fs_input - self.__obfuscate_enc):
                common.exception("The given key file is too small.")
        else:
            fs_key = fs_input + self.__obfuscate_key


        common.build_task_file(self.__task_id, self.__file_input, fs_input,
                               self.__file_key, fs_key, self.__file_output,
                               fs_output, "encryption")

        keyfile.build_file_key(self.__file_key, fs_input,
                               self.__buffer_size, self.__obfuscate_key,
                               self.__existing_key, self.__dev_random,
                               self.__fortuna, self.__overwrite, 1)
        self.__file_size = fs_input
        self.__erfr_core()

        if int(self.__obfuscate_enc) > 0:
            obfuscator.add_random_bytes(
                self.__file_output, self.__buffer_size, self.__obfuscate_enc,
                self.__dev_random, self.__fortuna)

    def __erfr_core(self):
        """
            Core method for encryption/decryption.
        """
        delay = common.get_delay()

        fh_input = open(self.__file_input, "rb")
        fh_key = open(self.__file_key, "rb")
        fh_output = open(self.__file_output, "wb")

        byte_blocks = int(self.__file_size / self.__buffer_size)
        byte_remainder = self.__file_size % self.__buffer_size

        data_input = bytearray(b"")
        data_key = bytearray(b"")
        data_output = bytearray(b"")

        for block in range(byte_blocks):
            data_input.extend(fh_input.read(self.__buffer_size))
            data_key.extend(fh_key.read(self.__buffer_size))

            if self.__reverse:
                while len(data_input) >= self.__reverse_bytes:
                    data_output.extend(
                        self.__transform(data_input[0:self.__reverse_bytes],
                                         data_key[0:self.__reverse_bytes],
                                         delay))
                    data_input = data_input[self.__reverse_bytes::]
                    data_key = data_key[self.__reverse_bytes::]

                if len(data_output) >= self.__buffer_size:
                    fh_output.write(data_output[0:self.__buffer_size])
                    data_output = data_output[self.__buffer_size::]
            else:
                fh_output.write(self.__transform(data_input, data_key, delay))
                data_input = bytearray(b"")

        if byte_remainder > 0:
            data_input.extend(fh_input.read(byte_remainder))
            data_key.extend(fh_key.read(byte_remainder))

            if self.__reverse:
                while len(data_input) > 0:
                    if len(data_input) >= self.__reverse_bytes:
                        data_output.extend(
                            self.__transform(
                                data_input[0:self.__reverse_bytes],
                                           data_key[0:self.__reverse_bytes],
                                delay))
                        data_input = data_input[self.__reverse_bytes::]
                        data_key = data_key[self.__reverse_bytes::]
                    else:
                        data_output.extend(
                            self.__transform(data_input, data_key, delay))
                        break
            else:
                fh_output.write(self.__transform(data_input, data_key, delay))

            fh_output.write(data_output)

        fh_input.close()
        fh_key.close()
        fh_output.close()

    def __export(self, overwrite):
        """
            Core method to export encryption parameters into a config file.
        """
        if overwrite:
            if os.path.exists(self.__file_export):
                os.remove(self.__file_export)
        else:
            pv.path(self.__file_export, "export", True, False)


        relative_paths = bool(int(common.global_config(["Export"],
                                                       ["relative_paths"],
                                                       "0")))

        if relative_paths:
            file_input = self.__file_input.split(os.sep)[-1]
            file_key = self.__file_key.split(os.sep)[-1]
            file_output = self.__file_output.split(os.sep)[-1]
        else:
            file_input = self.__file_input
            file_key = self.__file_key
            file_output = self.__file_output

        f = self.__file_export
        s = "Erfr"
        parameter.write_option(f, s, "version", get_version(), True)
        s = "Task"
        if self.__task_id == None:
            parameter.write_option(f, s, "task_id", 0)
        else:
            parameter.write_option(f, s, "task_id", int(self.__task_id))
        s = "Files"
        parameter.write_option(f, s, "input_file", file_input)
        parameter.write_option(f, s, "key_file", file_key)
        parameter.write_option(f, s, "output_file", file_output)
        s = "Options"
        parameter.write_option(f, s, "buffer_size", int(self.__buffer_size))
        parameter.write_option( \
            f, s, "use_existing_key", int(self.__existing_key))
        parameter.write_option(f, s, "overwrite", int(self.__overwrite))
        s = "Obfuscation"
        parameter.write_option( \
            f, s, "obfuscate_enc",int(self.__obfuscate_enc))
        parameter.write_option( \
            f, s, "obfuscate_key", int(self.__obfuscate_key))
        s = "PRNG"
        parameter.write_option(f, s, "fortuna", int(self.__fortuna))
        parameter.write_option(f, s, "dev_random", int(self.__dev_random))
        s = "Rotation"
        if self.__rotate:
            parameter.write_option(f, s, "rotate_min", int(self.__rotate_min))
            parameter.write_option(f, s, "rotate_max", int(self.__rotate_max))
            parameter.write_option( \
                f, s, "rotate_step", int(self.__rotate_step))
            parameter.write_option(f, s, "rotate_mod", int(self.__rotate_mod))
        s = "Reversion"
        if self.__reverse:
            parameter.write_option( \
                f, s, "reverse_bytes", int(self.__reverse_bytes))
        s = "S-box"
        parameter.write_option(f, s, "sbox", int(self.__sbox))

    def __prepare_process(self, task_id, file_input, file_key, file_output,
                          buffer_size, existing_key, overwrite, obfuscate_enc,
                          obfuscate_key, fortuna, dev_random, rotate_min,
                          rotate_max, rotate_step, rotate_mod, reverse_bytes,
                          sbox, skip_checks):
        """
            Prepare the requested process by checking the given parameters
            and execute the appropriate method.
        """
        if not skip_checks:
            pv.path(file_input, "input", True, True)
            if not overwrite:
                if self.__encrypt:
                    pv.path(file_key, "key", True, existing_key)
                pv.path(file_output, "output", True, False)
            pv.compfile(file_input, "input", [[file_key, "key"],
                                              [file_output, "output"]])

        pv.intvalue(buffer_size, "buffer size", True, False, False)
        pv.intvalue(obfuscate_enc, "encrypted file obfuscation byte", True,
                    True, False)
        pv.intvalue(obfuscate_key, "key file obfuscation byte", True, True,
                    False)


        if rotate_min == None and rotate_max == None and rotate_step == None:
            self.__rotate = False
        else:
            pv.intvalue(rotate_min, "minimum rotation", True, True, False)
            pv.intvalue(rotate_max, "maximum rotation", True, True, False)
            pv.intvalue(rotate_min, "rotation step", True, False, True)
            range_value_min, range_value_max, range_value_step = \
                common.validate_range(rotate_min, rotate_max, rotate_step)
            self.__rotate = True

        if reverse_bytes == None:
            self.__reverse = False
        else:
            pv.intrange(reverse_bytes, "reverse byte", 2, None, False)
            self.__reverse = True

        self.__task_id = task_id
        self.__fortuna = fortuna
        self.__dev_random = dev_random
        self.__file_input = os.path.abspath(file_input)
        self.__file_key = os.path.abspath(file_key)
        self.__file_output = os.path.abspath(file_output)
        self.__buffer_size = int(buffer_size)
        self.__existing_key = existing_key
        self.__overwrite = overwrite
        self.__obfuscate_enc = int(obfuscate_enc)
        self.__obfuscate_key = int(obfuscate_key)
        self.__sbox = sbox

        if self.__rotate:
            self.__rotate_min = int(rotate_min)
            self.__rotate_max = int(rotate_max)
            self.__rotate_step = int(rotate_step)
            self.__rotate_mod = rotate_mod
            self.__rotate_obj = rt.Rotate(self.__rotate_min,
                                          self.__rotate_max,
                                          self.__rotate_step,
                                          self.__rotate_mod)
        if self.__reverse:
            self.__reverse_bytes = int(reverse_bytes)

    def __reset(self):
        """
            Reset private instance variables.
        """
        self.__task_id = None
        self.__encrypt = True
        self.__fortuna = False
        self.__dev_random = False
        self.__file_input = None
        self.__file_key = None
        self.__file_output = None
        self.__file_size = 0
        self.__file_export = None
        self.__buffer_size = 4096
        self.__existing_key = False
        self.__overwrite = False
        self.__obfuscate_enc = 0
        self.__obfuscate_key = 0
        self.__rotate = None
        self.__rotate_min = 0
        self.__rotate_max = 0
        self.__rotate_step = 0
        self.__rotate_mod = True
        self.__rotate_obj = None
        self.__reverse = False
        self.__reverse_bytes = 0
        self.__sbox = False

    def __transform(self, data_input, data_key, delay):
        """
            Core method to manipulate the input bytes.
        """
        data_output = bytearray(b"")

        if not self.__encrypt:
            if self.__reverse:
                data_input.reverse()
            if self.__rotate:
                data_input = self.__rotate_obj.rotate_bytes(self.__encrypt,
                                                            data_input)

        for byte_input, byte_key in zip(data_input, data_key):
            if self.__sbox:
                if self.__encrypt:
                    data_output.append(
                        sbox.FSB_RIJNDAEL[byte_input] ^ byte_key)
                else:
                    data_output.append(
                        sbox.ISB_RIJNDAEL[byte_input ^ byte_key])
            else:
                data_output.append(byte_input ^ byte_key)

        if self.__encrypt:
            if self.__rotate:
                data_output = self.__rotate_obj.rotate_bytes(self.__encrypt,
                                                             data_output)
            if self.__reverse:
                data_output.reverse()

        time.sleep(delay)

        return data_output

# EOF

#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# ============================================================================
# Erfr - One-time pad encryption tool
# Random byte generator core module
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

def get_prng(dev_random=False, fortuna=False, fortuna_seed_bytes=None,
             fortuna_reseed_period=None):
    """
        Create an instance of the requested pseudo-random number generator.
    """
    fallback = bool(int(common.global_config(["KeyGenerator", "General"],
                                             ["fallback"], "0")))
    prng = None

    try:
        if dev_random:
            prng = __DevRandom()
        else:
            prng = __Urandom()

        if fortuna:
            if fortuna_seed_bytes == None:
                try:
                    fortuna_seed_bytes = \
                        int(common.global_config(["Fortuna"], ["seed_bytes"],
                                                 16))
                except:
                    fortuna_seed_bytes = 16

            if fortuna_reseed_period == None:
                try:
                    fortuna_reseed_period = \
                        int(common.global_config(["Fortuna"], ["reseed_period"],
                                                 8))
                except:
                    fortuna_reseed_period = 8

            if fortuna_seed_bytes < 1:
                fortuna_seed_bytes = 1

            return __Fortuna(prng, fortuna_seed_bytes, fortuna_reseed_period)
        else:
            # The parameters for the seed bytes as well as the reseed period
            # are not relvant here and will be ignored.
            return prng
    except Exception as ex:
        if fallback:
            return __Urandom()
        else:
            common.exception(ex.message)

class __DevRandom(object):
    """
        Class to generate random bytes using "/dev/random".
    """
    def __init__(self):
        if not os.path.exists("/dev/random"):
            common.exception("The device \"/dev/random\" is available on " \
                             "Unix-like systems, only.")

    def get_bytes(self, amount):
        """
            Get a certain amount of pseudo-random bytes.
        """
        fh_random = open("/dev/random", "rb")
        bytes_random = bytearray(b"" + fh_random.read(amount))
        fh_random.close()

        return bytes_random

class __Fortuna(object):
    """
        Class to generate random bytes using the Fortuna pseudo-random number
        generator.
    """
    __crypto_version = None
    __fortuna = None
    __fortuna_reseed_count = 0
    __fortuna_reseed_period = 0
    __fortuna_seed_bytes = 0
    __randgen = None

    def __init__(self, prng, seed_bytes, reseed_period):
        try:
            import Crypto
            self.__crypto_version = "%s.%s.%s" % (Crypto.version_info[0],
                                                  Crypto.version_info[1],
                                                  Crypto.version_info[2])
        except ImportError:
            common.exception("The PyCrypto library does not seem to be " + \
                             "installed. Due to this, the Fortuna pseudo-" + \
                             "random number generator is unavailable.")

        try:
            from Crypto import Random
            self.__fortuna = Random.Fortuna.FortunaGenerator.AESGenerator()
        except ImportError:
            common.exception("The PyCrypto library seems to be " + \
                             "installed, but certain components cannot " + \
                             "be accessed. Please ensure that the " + \
                             "PyCrypto library (version 2.1.0 or higher) " + \
                             "has been installed properly.")

        self.__fortuna_seed_bytes = int(seed_bytes)
        self.__fortuna_reseed_period = int(reseed_period)
        self.__randgen = prng

    def get_bytes(self, amount):
        """
            Get a certain amount of pseudo-random bytes.
        """
        pv.intvalue(amount, "random bytes", True, False, False)
        amount = int(amount)

        if self.__fortuna_reseed_count == 0 or \
           self.__fortuna_reseed_count >= self.__fortuna_reseed_period:
            try:
                self.__fortuna.reseed(
                    self.__randgen.get_bytes(self.__fortuna_seed_bytes))
            except TypeError:
                common.exception("Version mismatch?")

            if self.__fortuna_reseed_count >= self.__fortuna_reseed_period:
                self.__fortuna_reseed_period = 1
            else:
                self.__fortuna_reseed_period += 1

        bytes_random = \
            bytearray(b"" + self.__fortuna.pseudo_random_data(amount))

        return bytes_random

class __Urandom(object):
    """
        Class to generate random bytes using the "os.urandom()" method.
    """
    def __init__(self):
        return

    def get_bytes(self, amount):
        """
            Get a certain amount of pseudo-random bytes.
        """
        bytes_random = bytearray(b"" + os.urandom(amount))

        return bytes_random

# EOF


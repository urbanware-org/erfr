#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ============================================================================
# Erfr - One-time pad encryption tool
# Byte rotation core module
# Copyright (C) 2018 by Ralf Kilian
# Distributed under the MIT License (https://opensource.org/licenses/MIT)
#
# Website: http://www.urbanware.org
# GitHub: https://github.com/urbanware-org/erfr
# ============================================================================


__version__ = "4.3.3"

from . import common

def get_version():
    """
        Return the version of this module.
    """
    return __version__

class Rotate(object):
    """
        Class for rotating bytes.
    """
    __increase = None
    __modulo = None

    __min = 0
    __max = 0
    __step = 0
    __init = 0
    __current = 0

    def __init__(self, minimum, maximum, step, modulo):
        """
            Constructor of the class.
        """
        self.__min, self.__max, self.__step = \
            common.validate_range(minimum, maximum, step)
        self.__init = (self.__max - self.__min) + 1

        if step > 0:
            self.__increase = True
            self.__current = minimum
        else:
            self.__increase = False
            self.__current = maximum
        self.__modulo = modulo

    def rotate_bytes(self, encrypt, data_input):
        """
            Method to rotate bytes.
        """
        data_output = bytearray(b"")

        if not self.__increase:
            self.__current = self.__current * -1

        for byte in data_input:
            if encrypt:
                data_output.append((byte + self.__current) % 256)
            else:
                data_output.append((byte - self.__current) % 256)

            if self.__modulo:
                self.__current += self.__step
                if self.__current > self.__max or self.__current < self.__min:
                    self.__current = ((self.__current - self.__min) % \
                                      self.__init) + self.__min
            else:
                if self.__increase:
                    self.__current += self.__step
                    if self.__current > self.__max:
                        self.__current = self.__min
                else:
                    self.__current -= self.__step
                    if self.__current < self.__min:
                        self.__current = self.__max

        return data_output

# EOF

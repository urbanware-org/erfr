#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# ============================================================================
# Erfr - One-time pad encryption tool
# Parameter file parser core module
# Copyright (C) 2018 by Ralf Kilian
# Distributed under the MIT License (https://opensource.org/licenses/MIT)
#
# Website: http://www.urbanware.org
# GitHub: https://github.com/urbanware-org/erfr
# ============================================================================

__version__ = "4.3.3"

import ConfigParser
import paval as pv

def get_version():
    """
        Return the version of this module.
    """
    return __version__

def read_option(file_path, section, option, fallback=None, empty=True):
    """
        Parse parameter file and read out the value of a certain option.
    """
    pv.path(file_path, "parameter", True, True)
    pv.string(section, "section string")
    pv.string(option, "option string")

    c = ConfigParser.RawConfigParser()
    c.read(file_path)

    value = ""
    try:
        value = c.get(section, option)
    except ConfigParser.NoSectionError:
        if fallback:
            return str(fallback)
        else:
            pass
    except ConfigParser.NoOptionError:
        if fallback:
            return str(fallback)
        else:
            pass

    try:
        int(value)
        return int(value)
    except:
        value = str(value)
        if len(value) > 0:
            return value
        else:
            if empty:
                return value
            else:
                if fallback == None:
                    return None
                else:
                    return str(fallback)

def remove_option(file_path, section, option):
    """
        Remove a certain option from a section inside the parameter file.
    """
    pv.path(file_path, "parameter", True, True)
    pv.string(section, "section string")
    pv.string(option, "option string")

    c = ConfigParser.RawConfigParser()
    c.read(file_path)

    c.remove_option(section, option)
    with open(file_path, 'w') as fh_parameter:
        c.write(fh_parameter)

def remove_section(file_path, section):
    """
        Remove a certain section from the parameter file.
    """
    pv.path(file_path, "parameter", True, True)
    pv.string(section, "section string")

    c = ConfigParser.RawConfigParser()
    c.read(file_path)

    c.remove_section(section)
    with open(file_path, 'w') as fh_parameter:
        c.write(fh_parameter)

def write_option(file_path, section, option, value="", new_file=False):
    """
        Write an option into a parameter file.
    """
    if not new_file:
        pv.path(file_path, "parameter", True, True)
    pv.string(section, "section string")
    pv.string(option, "option string")

    c = ConfigParser.RawConfigParser()
    c.read(file_path)

    if not section in c.sections():
        c.add_section(section)

    c.set(section, option, value)
    with open(file_path, 'w') as fh_parameter:
        c.write(fh_parameter)

# EOF


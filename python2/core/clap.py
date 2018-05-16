#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# ============================================================================
# Clap - Command-line argument parser module
# Copyright (C) 2017 by Ralf Kilian
# Distributed under the MIT License (https://opensource.org/licenses/MIT)
#
# Website: http://www.urbanware.org
# GitHub: https://github.com/urbanware-org/clap
# ============================================================================

__version__ = "1.1.9"

def get_version():
    """
        Return the version of this module.
    """
    return __version__

class Parser(object):
    """
        Project independent command-line argument parser class.
    """
    __arg_grp_opt = None
    __arg_grp_req = None
    __arg_parser = None
    __is_argparser = False
    __conflict_handler = "resolve"  # used by OptionParser, only

    def __init__(self):
        try:
            from argparse import ArgumentParser
            self.__arg_parser = ArgumentParser(add_help=False)
            self.__arg_grp_req = \
                self.__arg_parser.add_argument_group("required arguments")
            self.__arg_grp_opt = \
                self.__arg_parser.add_argument_group("optional arguments")
            self.__is_argparser = True
            return
        except ImportError:
            # Ignore the exception and proceed with the fallback
            pass

        try:
            from optparse import OptionParser
            self.__arg_parser = \
                OptionParser(conflict_handler=self.__conflict_handler)
            self.__arg_grp_req = \
                self.__arg_parser.add_option_group("Required arguments")
            self.__arg_grp_opt = \
                self.__arg_parser.add_option_group("Optional arguments")
            return
        except ImportError:
            # This should never happen
            raise ImportError("Failed to initialize an argument parser.")

    def add_avalue(self, arg_short, arg_long, arg_help, arg_dest, arg_default,
                   arg_required):
        """
            Add an argument that expects a single user-defined value.
        """
        if arg_required:
            obj = self.__arg_grp_req
        else:
            obj = self.__arg_grp_opt

        if not arg_default == None:
            # Enclose the value with quotes in case it is not an integer
            quotes = "'"
            try:
                arg_default = int(arg_default)
                quotes = ""
            except ValueError:
                pass

            if arg_help.strip().endswith(")"):
                arg_help = arg_help.rstrip(")")
                arg_help += ", default is %s%s%s)" % \
                    (quotes, str(arg_default), quotes)
            else:
                arg_help += " (default is %s%s%s)" % \
                    (quotes, str(arg_default), quotes)

        if self.__is_argparser:
            if arg_short == None:
                obj.add_argument(arg_long, help=arg_help, dest=arg_dest,
                                 default=arg_default, required=arg_required)
            else:
                obj.add_argument(arg_short, arg_long, help=arg_help,
                                 dest=arg_dest, default=arg_default,
                                 required=arg_required)
        else:
            if arg_short == None:
                obj.add_option(arg_long, help=arg_help, dest=arg_dest,
                               default=arg_default)
            else:
                obj.add_option(arg_short, arg_long, help=arg_help,
                               dest=arg_dest, default=arg_default)

    def add_predef(self, arg_short, arg_long, arg_help, arg_dest, arg_choices,
                   arg_required):
        """
            Add an argument that expects a certain predefined value.
        """
        if arg_required:
            obj = self.__arg_grp_req
        else:
            obj = self.__arg_grp_opt

        if self.__is_argparser:
            if arg_short == None:
                obj.add_argument(arg_long, help=arg_help, dest=arg_dest,
                                 choices=arg_choices, required=arg_required)
            else:
                obj.add_argument(arg_short, arg_long, help=arg_help,
                                 dest=arg_dest, choices=arg_choices,
                                 required=arg_required)
        else:
            if arg_short == None:
                obj.add_option(arg_long, help=arg_help, dest=arg_dest,
                               choices=arg_choices)
            else:
                # The OptionParser does not print the values to choose from,
                # so these have to be added manually to the description of
                # the argument first
                arg_help += " (choose from "
                for item in arg_choices:
                    arg_help += "'%s', " % item
                arg_help = arg_help.rstrip(", ") + ")"

                obj.add_option(arg_short, arg_long, help=arg_help,
                               dest=arg_dest)

    def add_switch(self, arg_short, arg_long, arg_help, arg_dest, arg_store,
                   arg_required):
        """
            Add an argument that does not expect anything, but returns a
            boolean value.
        """
        if arg_required:
            obj = self.__arg_grp_req
        else:
            obj = self.__arg_grp_opt

        if arg_store:
            arg_store = "store_true"
        else:
            arg_store = "store_false"

        if self.__is_argparser:
            if arg_short == None:
                obj.add_argument(arg_long, help=arg_help, dest=arg_dest,
                                 action=arg_store, required=arg_required)
            else:
                obj.add_argument(arg_short, arg_long, help=arg_help,
                                 dest=arg_dest, action=arg_store,
                                 required=arg_required)
        else:
            if arg_short == None:
                obj.add_option(arg_long, help=arg_help, dest=arg_dest,
                               action=arg_store)
            else:
                obj.add_option(arg_short, arg_long, help=arg_help,
                               dest=arg_dest, action=arg_store)

    def dependency(self, arg_name, arg_value, dependency):
        """
            Check the dependency of a command-line argument.
        """
        if not dependency == None:
            if arg_value == None or str(arg_value) == "":
                raise Exception("The '%s' argument depends on %s'." % \
                                (arg_name, dependency))

    def error(self, obj):
        """
            Raise an error and cause the argument parser to print the error
            message.
        """
        if type(obj) == str:
            obj = obj.strip()

        self.__arg_parser.error(obj)

    def parse_args(self):
        """
            Parse and return the command-line arguments.
        """
        if self.__is_argparser:
            args = self.__arg_parser.parse_args()
        else:
            (args, values) = self.__arg_parser.parse_args()
        return args

    def print_help(self):
        """
            Print the usage, description, argument details and epilog.
        """
        self.__arg_parser.print_help()

    def set_description(self, string):
        """
            Set the description text.
        """
        self.__arg_parser.description = string.strip()

    def set_epilog(self, string):
        """
            Set the epilog text.
        """
        self.__arg_parser.epilog = string.strip()

# EOF


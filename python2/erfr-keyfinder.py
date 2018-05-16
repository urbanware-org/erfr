#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# ============================================================================
# Erfr - One-time pad encryption tool
# Key Finder script
# Copyright (C) 2018 by Ralf Kilian
# Distributed under the MIT License (https://opensource.org/licenses/MIT)
#
# Website: http://www.urbanware.org
# GitHub: https://github.com/urbanware-org/erfr
# ============================================================================

import os
import sys

def main():
    from core import clap
    from core import keyfile
    from datetime import datetime as dt

    try:
        p = clap.Parser()
    except Exception as e:
        print "%s: error: %s" % (os.path.basename(sys.argv[0]), e)
        sys.exit(1)

    p.set_description("Find the corresponding key for an encrypted file " \
                      "and vice versa.")
    p.set_epilog("Further information and usage examples can be found " \
                 "inside the documentation file for this script.")

    # Define required arguments
    p.add_avalue("-d", "--directory", "directory to check for the " \
                 "corresponding files", "directory", None, True)
    p.add_avalue("-f", "--file", "file to compare (either the key or the " \
                 "encrypted file)", "input_file", None, True)

    # Define optional arguments
    p.add_switch("-h", "--help", "print this help message and exit", None,
                 True, False)
    p.add_switch("-i", "--ignore-read-errors", "ignore read errors inside "\
                 "given directory", "ignore_read_errors", True, False)
    p.add_switch(None, "--version", "print the version number and exit", None,
                 True, False)
    p.add_avalue("-e", "--obfuscate-enc", "number of bytes used to " \
                 "obfuscate the encrypted file", "obfuscate_enc", 0, False)
    p.add_avalue("-k", "--obfuscate-key", "number of bytes used to " \
                 "obfuscate the key file", "obfuscate_key", 0, False)

    if len(sys.argv) == 1:
        p.error("At least one required argument is missing.")
    elif ("-h" in sys.argv) or ("--help" in sys.argv):
        p.print_help()
        sys.exit(0)
    elif "--version" in sys.argv:
        print keyfile.get_version()
        sys.exit(0)

    args = p.parse_args()
    if args.ignore_read_errors == None:
        args.ignore_read_errors = False

    try:
        timestamp = dt.now()
        list_matches = keyfile.compare_files(args.input_file, args.directory,
                                             args.ignore_read_errors,
                                             args.obfuscate_enc,
                                             args.obfuscate_key)
        if len(list_matches) == 0:
            print "\nNo matches found for \"%s\"." % args.input_file
        else:
            if len(list_matches) == 1:
                print "\nFound one possible match for \"%s\":\n" \
                      % args.input_file
            else:
                print "\nFound %s possible matches for \"%s\":\n" \
                      % (str(len(list_matches)), args.input_file)
            print "-" * 78
            for match in list_matches:
                print "%s" % match
            print "-" * 78
        print "\nElapsed time: %s" % (dt.now() - timestamp)
    except Exception as e:
        p.error(e)

if __name__ == "__main__":
    main()

# EOF


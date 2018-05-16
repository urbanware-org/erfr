#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ============================================================================
# Erfr - One-time pad encryption tool
# Key Splitter script
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
        print("%s: error: %s" % (os.path.basename(sys.argv[0]), e))
        sys.exit(1)

    p.set_description("Split a key file into seperate parts and merge " \
                      "multiple key file parts to a single key file.")
    p.set_epilog("Further information and usage examples can be found " \
                 "inside the documentation file for this script.")

    # Define required arguments
    p.add_predef("-a", "--action", "action to perform", "action",
                 ["merge", "split"], True)
    p.add_avalue("-k", "--key-file", "key file path", "key_file", None, True)

    # Define optional arguments
    p.add_avalue("-b", "--buffer-size", "buffer size in bytes", "buffer_size",
                 4096, False)
    p.add_switch("-h", "--help", "print this help message and exit", None,
                 True, False)
    p.add_switch(None, "--overwrite", "overwrite existing file", "overwrite",
                 True, False)
    p.add_avalue("-p", "--parts", "split key into separate parts", "parts",
                 1, False)
    p.add_switch(None, "--version", "print the version number and exit", None,
                 True, False)

    if len(sys.argv) == 1:
        p.error("At least one required argument is missing.")
    elif ("-h" in sys.argv) or ("--help" in sys.argv):
        p.print_help()
        sys.exit(0)
    elif "--version" in sys.argv:
        print(keyfile.get_version())
        sys.exit(0)

    args = p.parse_args()
    if args.action == "merge" and args.parts > 1:
        p.error("The parts argument does not make any sense when merging " \
                "files.")

    try:
        timestamp = dt.now()
        if args.action == "split":
            keyfile.split_key(args.key_file, args.parts, args.buffer_size,
                              args.overwrite)
        else:
            keyfile.merge_key(args.key_file, args.buffer_size, args.overwrite)
        print("Elapsed time: %s" % (dt.now() - timestamp))
    except Exception as e:
        p.error(e)

if __name__ == "__main__":
    main()

# EOF

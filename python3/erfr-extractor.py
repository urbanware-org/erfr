#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ============================================================================
# Erfr - One-time pad encryption tool
# Extractor script
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
    from core import common
    from datetime import datetime as dt

    try:
        p = clap.Parser()
    except Exception as e:
        print("%s: error: %s" % (os.path.basename(sys.argv[0]), e))
        sys.exit(1)

    p.set_description("Extract a user-defined byte range from an existing " \
                      "into a new file.")
    p.set_epilog("Further information and usage examples can be found " \
                 "inside the documentation file for this script.")

    # Define required arguments
    p.add_avalue("-i", "--input-file", "input file path", "input_file", None,
                 True)
    p.add_avalue("-l", "--length", "number of bytes to read", "length", None,
                 True)
    p.add_avalue("-o", "--output-file", "output file path", "output_file",
                 None, True)
    p.add_avalue("-s", "--offset", "position where to start reading",
                 "offset", None, True)

    # Define optional arguments
    p.add_avalue("-b", "--buffer-size", "buffer size in bytes", "buffer_size",
                 4096, False)
    p.add_switch("-h", "--help", "print this help message and exit", None,
                 True, False)
    p.add_switch(None, "--overwrite", "overwrite existing file", "overwrite",
                 True, False)
    p.add_switch("-r", "--remove", "remove the extracted data from the " \
                 "input file", "remove_bytes", True, False)
    p.add_switch(None, "--version", "print the version number and exit", None,
                 True, False)

    if len(sys.argv) == 1:
        p.error("At least one required argument is missing.")
    elif ("-h" in sys.argv) or ("--help" in sys.argv):
        p.print_help()
        sys.exit(0)
    elif "--version" in sys.argv:
        print(common.get_version())
        sys.exit(0)

    args = p.parse_args()
    remove_bytes = None

    force_remove = \
        bool(int(common.global_config(["Extractor"], ["force_remove"], "0")))
    if force_remove:
        remove_bytes = True
    else:
        remove_bytes = args.remove_bytes

    try:
        timestamp = dt.now()
        common.extract_bytes(args.input_file, args.output_file, args.offset,
                             args.length, args.buffer_size, args.overwrite,
                             remove_bytes)
        print("Elapsed time: %s" % (dt.now() - timestamp))
    except Exception as e:
        p.error(e)

if __name__ == "__main__":
    main()

# EOF


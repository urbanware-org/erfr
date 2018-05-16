#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ============================================================================
# Erfr - One-time pad encryption tool
# Monitor script
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
    from core import monitor

    try:
        p = clap.Parser()
    except Exception as e:
        print("%s: error: %s" % (os.path.basename(sys.argv[0]), e))
        sys.exit(1)

    p.set_description("Return or monitor the current status of an Erfr " \
                      "encryption, decryption, key generation or file " \
                      "obfuscation process.")
    p.set_epilog("Further information and usage examples can be found " \
                 "inside the documentation file for this script.")

    # Define required arguments
    p.add_avalue("-t", "--task-id", "Erfr task ID", "task_id", None, True)

    # Define optional arguments
    p.add_avalue("-d", "--delay", "auto-refresh delay in seconds", "delay", 0,
                 False)
    p.add_switch("-h", "--help", "print this help message and exit", None,
                 True, False)
    p.add_switch(None, "--version", "print the version number and exit", None,
                 True, False)

    if len(sys.argv) == 1:
        p.error("At least one required argument is missing.")
    elif ("-h" in sys.argv) or ("--help" in sys.argv):
        p.print_help()
        sys.exit(0)
    elif "--version" in sys.argv:
        print(monitor.get_version())
        sys.exit(0)

    args = p.parse_args()
    try:
        monitor.get_status(args.task_id, args.delay)
    except Exception as e:
        p.error(e)

if __name__ == "__main__":
    main()

# EOF


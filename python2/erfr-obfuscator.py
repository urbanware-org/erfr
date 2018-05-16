#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# ============================================================================
# Erfr - One-time pad encryption tool
# Obfuscator script
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
    from core import obfuscator
    from datetime import datetime as dt

    try:
        p = clap.Parser()
    except Exception as e:
        print "%s: error: %s" % (os.path.basename(sys.argv[0]), e)
        sys.exit(1)

    p.set_description("Obfuscate existing encrypted and key files by " \
                      "adding random bytes.")
    p.set_epilog("Further information and usage examples can be found " \
                 "inside the documentation file for this script.")

    # Define required arguments
    p.add_avalue("-f", "--file", "target file path", "file", None, True)
    p.add_avalue("-r", "--random-bytes", "amount of random bytes to add to " \
                 "the given file", "random_bytes", 0, True)

    # Define optional arguments
    p.add_avalue("-b", "--buffer-size", "buffer size in bytes", "buffer_size",
                 4096, False)
    p.add_switch(None, "--dev-random", "use \"/dev/random\" as random " \
                 "number generator (Unix-like systems only)", "dev_random",
                 True, False)
    p.add_switch(None, "--fortuna", "use Fortuna as random number generator",
                 "fortuna", True, False)
    p.add_switch("-h", "--help", "print this help message and exit", None,
                 True, False)
    p.add_avalue("-t", "--task-id", "user-defined task ID", "task_id", None,
                 False)
    p.add_switch(None, "--version", "print the version number and exit", None,
                 True, False)

    if len(sys.argv) == 1:
        p.error("At least one required argument is missing.")
    elif ("-h" in sys.argv) or ("--help" in sys.argv):
        p.print_help()
        sys.exit(0)
    elif "--version" in sys.argv:
        print obfuscator.get_version()
        sys.exit(0)

    args = p.parse_args()
    try:
        task_id = common.get_task_id(args.task_id)
    except Exception as e:
        task_id = args.task_id
        p.error(e)

    try:
        timestamp = dt.now()
        common.status(task_id, "file obfuscation", "start")
        obfuscator.obfuscate_file(task_id, args.file, args.buffer_size,
                                  args.random_bytes, args.dev_random,
                                  args.fortuna)
        common.status(task_id, "file obfuscation", "finish")
        print "Elapsed time: %s" % (dt.now() - timestamp)
    except Exception as e:
        common.status(task_id, "file obfuscation", "cancel")
        p.error(e)
    finally:
        common.delete_temp_files(task_id)

if __name__ == "__main__":
    main()

# EOF

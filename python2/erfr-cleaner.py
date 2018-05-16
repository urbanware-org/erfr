#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# ============================================================================
# Erfr - One-time pad encryption tool
# Cleaner script
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

    try:
        p = clap.Parser()
    except Exception as e:
        print "%s: error: %s" % (os.path.basename(sys.argv[0]), e)
        sys.exit(1)

    p.set_description("Delete remaining temporary files of the Erfr " \
                      "components.")
    p.set_epilog("Further information and usage examples can be found " \
                 "inside the documentation file for this script.")

    # Define optional arguments
    p.add_switch("-h", "--help", "print this help message and exit", None,
                 True, False)
    p.add_switch(None, "--version", "print the version number and exit", None,
                 True, False)

    if ("-h" in sys.argv) or ("--help" in sys.argv):
        p.print_help()
        sys.exit(0)
    elif "--version" in sys.argv:
        print common.get_version()
        sys.exit(0)

    try:
        print "Started cleaning up temporary files."
        max_tasks = int(common.get_max_tasks())
        for task in range(1, max_tasks + 1):
            common.delete_temp_files(task)
        print "Finished cleaning up temporary files."
    except Exception as e:
        print "cancelled cleaning up temporary files."
        p.error(e)

if __name__ == "__main__":
    main()

# EOF


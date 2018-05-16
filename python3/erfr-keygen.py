#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ============================================================================
# Erfr - One-time pad encryption tool
# Key Generator script
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
    from core import keyfile
    from datetime import datetime as dt

    try:
        p = clap.Parser()
    except Exception as e:
        print("%s: error: %s" % (os.path.basename(sys.argv[0]), e))
        sys.exit(1)

    p.set_description("Generate key files which can either be used for " \
                      "encryption or obfuscation purposes (as fake key " \
                      "files).")
    p.set_epilog("Further information and usage examples can be found " \
                 "inside the documentation file for this script.")

    # Define required arguments
    p.add_avalue("-s", "--key-size", "key size in bytes", "key_size", None,
                 True)

    # Define optional arguments
    p.add_switch(None, "--base64", "generate Base64 key string", "base64",
                 True, False)
    p.add_avalue("-b", "--buffer-size", "buffer size in bytes", "buffer_size",
                 4096, False)
    p.add_switch(None, "--dev-random", "use \"/dev/random\" as random " \
                 "number generator (Unix-like systems only)", "dev_random",
                 True, False)
    p.add_switch(None, "--fortuna", "use Fortuna as random number generator",
                 "fortuna", True, False)
    p.add_switch("-h", "--help", "print this help message and exit", None,
                 True, False)
    p.add_avalue("-k", "--key-file", "key file path", "key_file", None, False)
    p.add_switch(None, "--overwrite", "overwrite existing file", "overwrite",
                 True, False)
    p.add_avalue("-p", "--parts", "split key into separate parts", "parts", 1,
                 False)
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
        print(keyfile.get_version())
        sys.exit(0)

    args = p.parse_args()
    if not args.base64 and args.key_file == None:
        p.error("The argument to either generate a key file or a Base64 " \
                "encoded key string is missing.")
    elif args.base64 and not args.key_file == None:
        p.error("The arguments to generate a key file and a Base64 key " \
                "string cannot be given at the same time.")
    elif args.base64 and args.overwrite:
        p.error("The overwrite argument does not make any sense when " \
                "generating a Base64 string.")
    elif args.base64 and args.parts > 1:
        p.error("The parts argument does not make any sense when " \
                "generating a Base64 string.")

    if args.base64:
        if not args.task_id == None:
            p.error("No task ID can be given when creating a Base64 key " \
                    "string.")
        try:
            print(keyfile.generate_key_string(args.key_size, args.dev_random,
                                              args.fortuna))
        except Exception as e:
            p.error(e)
    else:
        try:
            task_id = common.get_task_id(args.task_id)
        except Exception as e:
            task_id = args.task_id
            p.error(e)

        try:
            timestamp = dt.now()
            common.status(task_id, "key generation", "start")
            keyfile.generate_key_file(task_id, args.key_file, args.key_size,
                                      args.buffer_size, 0, False,
                                      args.dev_random, args.fortuna,
                                      args.overwrite, args.parts)
            common.status(task_id, "key generation", "finish")
            print("Elapsed time: %s" % (dt.now() - timestamp))
        except Exception as e:
            common.status(task_id, "key generation", "cancel")
            p.error(e)
        finally:
            common.delete_temp_files(task_id)

if __name__ == "__main__":
    main()

# EOF


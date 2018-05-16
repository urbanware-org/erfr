#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# ============================================================================
# Erfr - One-time pad encryption tool
# Executor script
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
    from core import main as core
    from datetime import datetime as dt

    try:
        p = clap.Parser()
    except Exception as e:
        print "%s: error: %s" % (os.path.basename(sys.argv[0]), e)
        sys.exit(1)

    p.set_description("Process a parameter file generated by the main Erfr " \
                      "script containing encryption related information.")
    p.set_epilog("Further information and usage examples can be found " \
                 "inside the documentation file for this script.")

    # Define required arguments
    p.add_predef("-a", "--action", "action to perform", "action",
                 ["encrypt", "decrypt"], True)
    p.add_avalue("-f", "--file", "parameter file to process", "file", None,
                 True)

    # Define optional arguments (general)
    p.add_switch("-h", "--help", "print this help message and exit", None,
                 True, False)
    p.add_avalue("-s", "--suffix", "add additional suffix to the decrypted " \
                 "file", "suffix", None, False)
    p.add_switch(None, "--version", "print the version number and exit", None,
                 True, False)

    if len(sys.argv) == 1:
        p.error("At least one required argument is missing.")
    elif ("-h" in sys.argv) or ("--help" in sys.argv):
        p.print_help()
        sys.exit(0)
    elif "--version" in sys.argv:
        print core.get_version()
        sys.exit(0)

    args = p.parse_args()
    if args.action == None:
        p.error("The action argument is missing.")
    elif args.action.lower() == "encrypt":
        encrypt = True
    elif args.action.lower() == "decrypt":
        encrypt = False
    else:
        p.error("An unsupported action was given.")

    try:
        params = common.process_params(args.file)

        buffer_size = params.get("buffer_size")
        dev_random = params.get("dev_random")
        fortuna = params.get("fortuna")
        input_file = params.get("input_file")
        key_file = params.get("key_file")
        obfuscate_enc = params.get("obfuscate_enc")
        obfuscate_key = params.get("obfuscate_key")
        output_file = params.get("output_file")
        overwrite = params.get("overwrite")
        rotate_max = params.get("rotate_max")
        rotate_min = params.get("rotate_min")
        rotate_mod = params.get("rotate_mod")
        rotate_step = params.get("rotate_step")
        reverse_bytes = params.get("reverse_bytes")
        sbox = params.get("sbox")
        task_id = params.get("task_id")
        use_existing_key = params.get("use_existing_key")

        timestamp = dt.now()
        erfr = core.ErfrCrypt()

        if task_id == 0:
            task_id = None

        if encrypt:
            if not args.suffix == None:
                p.error("The argument for an additional suffix can only be " \
                        "used when decrypting a file.")
            common.status(task_id, "encryption", "start")
            erfr.encrypt_file(task_id, input_file, key_file, output_file,
                              buffer_size, use_existing_key, overwrite,
                              obfuscate_enc, obfuscate_key, fortuna,
                              dev_random, rotate_min, rotate_max, rotate_step,
                              rotate_mod, reverse_bytes, sbox)
            common.status(task_id, "encryption", "finish")
        else:
            if not args.suffix == None:
                input_file += ".%s" % args.suffix
            common.status(task_id, "decryption", "start")
            erfr.decrypt_file(task_id, output_file, key_file, input_file,
                              buffer_size, overwrite, obfuscate_enc,
                              obfuscate_key, rotate_min, rotate_max,
                              rotate_step, rotate_mod, reverse_bytes, sbox)
            common.status(task_id, "decryption", "finish")
        print "Elapsed time: %s" % (dt.now() - timestamp)
    except Exception as e:
        if encrypt:
            common.status(task_id, "encryption", "cancel")
        else:
            common.status(task_id, "decryption", "cancel")
        p.error(e)
    finally:
       try:
           common.delete_temp_files(task_id)
       except:
           pass

if __name__ == "__main__":
    main()

# EOF

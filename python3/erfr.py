#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ============================================================================
# Erfr - One-time pad encryption tool
# Main encryption/decryption script
# Copyright (C) 2018 by Ralf Kilian
# Distributed under the MIT License (https://opensource.org/licenses/MIT)
#
# Website: http://www.urbanware.org
# GitHub: https://github.com/urbanware-org/erfr
# ============================================================================

import os
import sys

def main():
    from core import common
    from core import main as core
    from core import keyfile
    from core import mainargs
    from datetime import datetime as dt

    try:
        p = mainargs.Parser()
    except Exception as e:
        print("%s: error: %s" % (os.path.basename(sys.argv[0]), e))
        sys.exit(1)

    p.set_description("Encrypt or decrypt a file using the one-time pad " \
                      "encryption method with optional features.")
    p.set_epilog("Further information and usage examples can be found " \
                 "inside the documentation file for this script.")

    # Define required arguments
    p.add_predef("-a", "--action", "action to perform", "action",
                 ["encrypt", "decrypt"], True, "required")
    p.add_avalue("-i", "--input-file", "input file path", "input_file", None,
                 True, "required")
    p.add_avalue("-k", "--key-file", "key file path", "key_file", None, True,
                 "required")
    p.add_avalue("-o", "--output-file", "output file path", "output_file",
                 None, True, "required")

    # Define optional arguments (general)
    p.add_switch(None, "--base64", "use a Base64 key string instead of a " \
                 "binary key file", "base64", True, False)
    p.add_avalue("-b", "--buffer-size", "buffer size in bytes", "buffer_size",
                 4096, False)
    p.add_switch(None, "--dev-random", "use \"/dev/random\" as random " \
                 "number generator (Unix-like systems only)", "dev_random",
                 True, False)
    p.add_avalue("-e", "--export", "Export encryption parameters into a file",
                 "export_file", None, False)
    p.add_switch(None, "--fortuna", "use Fortuna as random number generator",
                 "fortuna", True, False)
    p.add_switch("-h", "--help", "print this help message and exit", None,
                 True, False)
    p.add_switch(None, "--no-task-id", "disable the task ID", "no_task_id",
                 True, False)
    p.add_avalue(None, "--obfuscate-enc", "obfuscate the encrypted file by " \
                 "adding random bytes", "obfuscate_enc", 0, False)
    p.add_avalue(None, "--obfuscate-key", "obfuscate the key file by " \
                 "adding random bytes", "obfuscate_key", 0, False)
    p.add_switch(None, "--overwrite", "overwrite existing files", "overwrite",
                 True, False)
    p.add_avalue("-t", "--task-id", "user-defined task ID", "task_id", None,
                 False)
    p.add_switch(None, "--use-existing-key", "use an already existing key " \
                 "for encryption", "use_existing_key", True, False)
    p.add_switch(None, "--version", "print the version number and exit", None,
                 True, False)

    # Define optional arguments for the rotate feature
    p.add_avalue(None, "--rotate-max", "maximum rotation value (0-255)",
                 "rotate_max", None, False, "rotate")
    p.add_avalue(None, "--rotate-min", "minimum rotation value (0-255)",
                 "rotate_min", None, False, "rotate")
    p.add_switch(None, "--rotate-modulo", "use modulo operation when using " \
                 "byte rotation", "rotate_mod", True, False, "rotate")
    p.add_avalue(None, "--rotate-step", "rotation step value", "rotate_step",
                 None, False, "rotate")

    # Define optional arguments for the reverse feature
    p.add_avalue("-r", "--reverse", "reverse certain amount of bytes",
                 "reverse_bytes", None, False, "reverse")

    # Define optional arguments for the substitution-box feature
    p.add_switch("-s", "--use-sbox", "use the Rijndael substitution-box to " \
                 "obscure the relationship between the key and the " \
                 "ciphertext", "sbox", True, False, "sbox")

    if len(sys.argv) == 1:
        p.error("At least one required argument is missing.")
    elif ("-h" in sys.argv) or ("--help" in sys.argv):
        p.print_help()
        sys.exit(0)
    elif "--version" in sys.argv:
        print(core.get_version())
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

    key_file = args.key_file
    use_existing_key = args.use_existing_key
    base64 = False

    if encrypt:
        if args.base64 and use_existing_key:
            p.error("The argument for using an existing key cannot be used " \
                    "together with the optional Base64 key argument.")

    if args.no_task_id:
        if not args.task_id == None:
            p.error("The argument for disabling the task ID cannot be used " \
                    "together with the user-defined task ID argument.")
        task_id = None
    else:
        try:
            task_id = common.get_task_id(args.task_id)
            if args.base64:
                key_file = keyfile.base64_key(task_id, args.key_file)
                if encrypt:
                    use_existing_key = True
                base64 = True
            else:
                key_file = args.key_file
        except Exception as e:
            task_id = args.task_id
            p.error(e)

    try:
        timestamp = dt.now()
        erfr = core.ErfrCrypt()

        if encrypt:
            if args.export_file == None:
                action = "encryption"
            else:
                action = "export"
            common.status(task_id, action, "start")
            erfr.encrypt_file(task_id, args.input_file, key_file,
                              args.output_file, args.buffer_size,
                              use_existing_key, args.overwrite,
                              args.obfuscate_enc, args.obfuscate_key,
                              args.fortuna, args.dev_random, args.rotate_min,
                              args.rotate_max, args.rotate_step,
                              args.rotate_mod, args.reverse_bytes,
                              args.sbox, args.export_file)
            common.status(task_id, action, "finish")
        else:
            if not args.export_file == None:
                p.error("The argument for exporting the encryption " \
                        "parameters into a file can only be used when " \
                        "encrypting a file.")

            if use_existing_key:
                p.error("The argument for using an existing key can " \
                        "only be used when encrypting a file.")
            elif args.dev_random or args.fortuna:
                p.error("Giving a random number generator only makes " \
                        "sense when encrypting a file.")
            else:
                common.status(task_id, "decryption", "start")
                erfr.decrypt_file(task_id, args.input_file, key_file,
                                  args.output_file, args.buffer_size,
                                  args.overwrite, args.obfuscate_enc,
                                  args.obfuscate_key, args.rotate_min,
                                  args.rotate_max, args.rotate_step,
                                  args.rotate_mod, args.reverse_bytes,
                                  args.sbox)
                common.status(task_id, "decryption", "finish")
        print("Elapsed time: %s" % (dt.now() - timestamp))
    except Exception as e:
        if encrypt:
            common.status(task_id, action, "cancel")
        else:
            common.status(task_id, "decryption", "cancel")
        p.error(e)
    finally:
        if base64:
            common.delete_file(key_file, "temporary key")
        common.delete_temp_files(task_id)

if __name__ == "__main__":
    main()

# EOF

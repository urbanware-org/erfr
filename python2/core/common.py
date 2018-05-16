#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# ============================================================================
# Erfr - One-time pad encryption tool
# Common core module
# Copyright (C) 2018 by Ralf Kilian
# Distributed under the MIT License (https://opensource.org/licenses/MIT)
#
# Website: http://www.urbanware.org
# GitHub: https://github.com/urbanware-org/erfr
# ============================================================================

__version__ = "4.3.3"

import base64
import ConfigParser
import os
import parameter
import paval as pv
import sys
import tempfile
import textwrap
import time

def build_task_file(task_id, file_input_path, file_input_size,
                    file_key_path, file_key_size, file_output_path,
                    file_output_size, process_type):
    """
        Build a temporary task file using the Erfr task ID containing the
        relevant information of the corresponding encryption or decryption
        ("crypt_process"), key generation or obfuscation process.
    """

    if task_id == None:
        return

    pv.intrange(task_id, "task ID", 1, get_max_tasks(), False)
    pv.intvalue(file_input_size, "input file size", True, False, False)

    if file_input_path == None:
        exception("The input file path is missing.")

    if "crypt" in process_type:
        pv.intvalue(file_key_size, "key file size", True, True, False)
        if file_key_path == None:
            exception("The key file path is missing.")

        pv.intvalue(file_output_size, "output file size", True, True, False)
        if file_output_path == None:
            exception("The output file path is missing.")

    task = __validate_files(file_input_path, file_key_path, file_output_path)
    if not task == 0:
        exception("At least one of the given files already is in use by " \
                  "another Erfr process with ID %s." % task)

    task_file = get_task_file(task_id)
    if file_exists(task_file):
        exception("The task file for the given ID already exists.")

    string = __build_content_string(file_input_path, file_input_size,
                                    file_key_path, file_key_size,
                                    file_output_path, file_output_size,
                                    process_type)

    encode_file = bool(int(global_config(["TaskID"], ["encode_base64"], 1)))

    # Check if the file shall be encoded and then run the appropriate code for
    # the Python framework used
    if encode_file:
        if sys.version_info[0] == 2:
            content = base64.encodestring(string)
        elif sys.version_info[0] > 2:
            temp = string.encode(sys.getdefaultencoding())
            content = base64.encodestring(temp)
    else:
        if sys.version_info[0] == 2:
            content = string
        elif sys.version_info[0] > 2:
            content = bytes(string, sys.getdefaultencoding())

    try:
        fh_task = open(task_file, "wb")
        fh_task.write(content)
        fh_task.close()
    except:
        print "Failed to create task file. Due to this, the monitor " + \
              "component will not work on this process."

def delete_file(file_path, name):
    """
        Delete a given file.
    """
    if file_exists(file_path):
        try:
            os.remove(file_path)
        except:
            exception("Could not delete the %s file." % name)

def delete_temp_files(task_id):
    """
        Delete the temporary files of an Erfr process using the corresponding
        Erfr task ID.
    """
    if task_id == None:
        return

    pv.intrange(task_id, "task ID", 1, get_max_tasks(), False)

    task_file = get_task_file(task_id)
    file_key = task_file.rstrip(".tmp") + ".key"

    delete_file(file_key, "temporary key")
    delete_file(task_file, "temporary task")

def exception(string):
    """
        Raise an exception and print a formatted error description.
    """
    temp = textwrap.wrap(string.strip(), 80)
    string = "\n" + "\n".join(temp)

    # Way-hay and up it raises,
    # Way-hay and up it raises,
    # Way-hay and up it raises,
    # Exception in the program
    raise Exception(string)

def extract_bytes(file_input, file_output, offset=0, length=0,
                  buffer_size=4096, overwrite=False, remove=False):
    """
        Extract a user-defined byte range into a separate file.
    """
    pv.path(file_input, "input", True, True)
    if not overwrite:
        pv.path(file_output, "output", True, False)
    pv.compfile(file_input, "input", [[file_output, "output"]])
    pv.intvalue(offset, "offset", True, True, False)
    pv.intvalue(length, "length", True, False, False)
    pv.intvalue(buffer_size, "buffer size", True, False, False)

    file_input = os.path.abspath(file_input)
    file_output = os.path.abspath(file_output)
    offset = int(offset)
    length = int(length)
    buffer_size = int(buffer_size)
    file_size = get_file_size(file_input)

    if (offset + length) > file_size:
        exception("With this offset the maximal length is %s bytes." % \
                   str(file_size - offset))

    __extract_bytes(file_input, file_output, offset, length, buffer_size,
                    remove)

def file_exists(file_path):
    """
        Simply return if a file exists.
    """
    exists = False
    if os.path.exists(file_path):
        if os.path.isfile(file_path):
            exists = True

    return exists

def get_delay():
    """
        Read out the set delay from the global configuration and validate it.
    """
    seconds = int(global_config(["General"], ["delay"], "0"))
    if seconds < 0:
        seconds = 0
    elif seconds > 100:
        seconds = 100

    delay = float(seconds) / 1000

    return delay

def get_file_size(file_path):
    """
        Get the size of a file in bytes.
    """
    pv.path(file_path, "", True, True)

    f = open(file_path, "rb")
    f.seek(0, 2)
    file_size = f.tell()
    f.close()

    return int(file_size)

def get_max_tasks():
    """
        Return the maximum number of Erfr tasks.
    """
    max_tasks = int(global_config(["TaskID"], ["max_tasks"], 1024))
    if max_tasks < 1:
        exception("The maximum number of Erfr tasks must not be less than " \
                  "zero.")

    return max_tasks

def get_task_file(task_id):
    """
        Get the task file path for the Erfr encryption or decryption
        process with the given task ID.
    """
    pv.intrange(task_id, "task ID", 1, get_max_tasks(), False)

    return os.path.join(tempfile.gettempdir(), "erfr_" + \
                        str(task_id).rjust(4, "0") + ".tmp")

def get_task_id(task_id):
    """
        Get a numeric task ID for an Erfr process or validate a given one.
    """
    disabled = \
        bool(int(global_config(["TaskID"], ["disable_permanently"], "0")))
    explicit = \
        bool(int(global_config(["TaskID"], ["explicit"], "0")))

    if disabled:
        return None
    elif explicit:
        if task_id == None:
            return None
        elif int(task_id) == 0:
            return None

    if task_id == None:
        for task in range(1, get_max_tasks() + 1):
            task_file = get_task_file(task)

            if file_exists(task_file):
                task_id = 0
            else:
                task_id = task
                break

        if task_id == 0:
            exception("All task IDs already are in use. Please wait for an " \
                      "Erfr process to complete before starting a new one.")
    elif int(task_id) == 0:
        task_id = None
    else:
        pv.intrange(task_id, "task ID", 1, get_max_tasks(), False)

        task_file = get_task_file(task_id)
        if file_exists(task_file):
            exception("The task file for the given task ID already exists.")

    return task_id

def get_version():
    """
        Return the version of this module.
    """
    return __version__

def global_config(sections=[], options=[], fallback=""):
    """
        Parse config file and read out the value of a certain option.
    """
    use_fallback = True

    c = ConfigParser.RawConfigParser()
    c.read(os.path.join(os.path.dirname(sys.argv[0]), "cfg", "global.cfg"))

    value = ""
    for section in sections:
        for option in options:
            try:
                value = c.get(section, option)
                use_fallback = False
                break
            except ConfigParser.NoSectionError:
                pass
            except ConfigParser.NoOptionError:
                pass

        if not use_fallback:
            break

    if use_fallback:
        value = fallback

    try:
        value = int(value)
    except:
        value = str(value)

    return value

def progress_bar(width=0, value=0, description="", padding=0, block_char="=",
                 status_char="", percent=False):
    """
        Draw a character based progress bar.
    """
    pv.intvalue(width, "width", True, False, False)
    pv.intvalue(value, "percent", True, True, False)
    pv.intvalue(padding, "padding", True, True, False)

    if len(description) > 0:
        description = description.ljust(padding, " ")
    if len(block_char) == 0:
        block_char = "="
    if len(status_char) > 0:
        status_char = status_char[0].rjust(2, " ")
        padding += 2
    if percent:
        pstatus = "(%s %%)".rjust(8, " ") % str(value).rjust(3, " ")
        padding += 8
    else:
        pstatus = ""

    blocks_max = width - (padding + 2)
    blocks = int((blocks_max * value) / 100)
    if blocks > blocks_max:
        blocks = blocks_max

    blocks_empty = blocks_max - blocks
    progress_bar = "%s[%s%s]%s%s" % \
        (description, (block_char * blocks), (" " * blocks_empty), pstatus,
         status_char)

    return progress_bar

def process_params(param_file):
    """
        Read and process the information read out from a parameter file.
    """

    if not os.path.exists(param_file):
        exception("The given parameter files does not exist.")

    params = {}

    f = param_file
    s = "Task"
    params.update({"task_id" : parameter.read_option(f, s, "task_id", None)})
    s = "Files"
    params.update( \
        {"input_file" : parameter.read_option(f, s, "input_file", None)})
    params.update( \
        {"key_file" : parameter.read_option(f, s, "key_file", None)})
    params.update( \
        {"output_file" : parameter.read_option(f, s, "output_file", None)})
    s = "Options"
    params.update( \
        {"buffer_size" : parameter.read_option(f, s, "buffer_size", 4096)})
    params.update( \
        {"use_existing_key" : bool(parameter.read_option(f, s, "existing_key",
         False))})
    params.update( \
        {"overwrite" : bool(parameter.read_option(f, s, "overwrite", False))})
    s = "Obfuscation"
    params.update( \
        {"obfuscate_enc" : parameter.read_option(f, s, "obfuscate_enc", 0)})
    params.update( \
        {"obfuscate_key" : parameter.read_option(f, s, "obfuscate_key", 0)})
    s = "PRNG"
    params.update( \
        {"fortuna" : bool(parameter.read_option(f, s, "fortuna", False))})
    params.update( \
        {"dev_random" : bool(parameter.read_option(f, s, "dev_random",
         False))})
    s = "Rotation"
    params.update( \
        {"rotate_min" : parameter.read_option(f, s, "rotate_min", None,
         False)})
    params.update( \
        {"rotate_max" : parameter.read_option(f, s, "rotate_max", None,
         False)})
    params.update( \
        {"rotate_step" : parameter.read_option(f, s, "rotate_step", None,
         False)})
    params.update( \
        {"rotate_mod" : parameter.read_option(f, s, "rotate_mod", 0, False)})
    s = "Reversion"
    params.update( \
        {"reverse_bytes" : parameter.read_option(f, s, "reverse_bytes", None,
         False)})
    s = "S-box"
    params.update( \
        {"sbox" : bool(parameter.read_option(f, s, "sbox", False))})

    return params

def status(task_id, process, status):
    """
        Print a status message on the terminal.
    """
    if task_id == None:
        return

    pv.intrange(task_id, "task ID", 1, get_max_tasks(), False)

    message = "%sed %s process with task ID %s." % \
              (str(status).capitalize(), str(process), str(task_id))

    while (" " * 2) in message:
        message = message.replace((" " * 2), " ")

    print message

def validate_range(range_value_min=0, range_value_max=0, range_value_step=0):
    """
        Validate byte range values.
    """
    pv.intvalue(range_value_max, "maximum byte range", True, False, False)
    range_value_max = int(range_value_max)
    pv.intrange(range_value_min, "minimum byte range", 1,
                (int(range_value_max) - 1), False)
    pv.intvalue(range_value_step, "step byte range", True, False, True)

    range_value_min = int(range_value_min)
    range_value_step = int(range_value_step)
    range_length = range_value_max - range_value_min

    if range_length < 4:
        exception("The range must at least have a length of 4.")

    range_max_step = int(range_length / 2)
    pv.intrange(range_value_step, "step byte range",
                (range_max_step * -1), range_max_step, False)

    return range_value_min, range_value_max, range_value_step

def __build_content_string(file_input_path, file_input_size, file_key_path,
                           file_key_size, file_output_path, file_output_size,
                           process_type):
    """
        Build the raw content string for the task file.
    """
    content = "type;%s\ninput;%s;%s" % \
              (process_type, str(file_input_size), file_input_path)

    if "crypt" in process_type:
        content += "\nkey;%s;%s\noutput;%s;%s" % \
                   (str(file_key_size), file_key_path, str(file_output_size),
                    file_output_path)

    return str(content)

def __extract_bytes(file_input, file_output, offset, length, buffer_size,
                    remove):
    """
        Core method to extract a byte range into a separate file.
    """
    delay = get_delay()

    fh_input = open(file_input, "rb")
    fh_output = open(file_output, "wb")

    byte_blocks = int(length / buffer_size)
    byte_remainder = length % buffer_size

    for block in range(byte_blocks):
        fh_input.seek(offset)
        data_input = bytearray(b"" + fh_input.read(buffer_size))
        fh_output.write(data_input)
        offset += buffer_size
        time.sleep(delay)

    if byte_remainder > 0:
        fh_input.seek(offset)
        data_input = bytearray(b"" + fh_input.read(byte_remainder))
        fh_output.write(data_input)
        time.sleep(delay)

    fh_input.close()
    fh_output.close()

    if remove:
        __remove_bytes_inplace(file_input, offset, length, buffer_size)

def __remove_bytes_inplace(file_input, offset, length, buffer_size):
    """
        Remove a certain amount of bytes from a file operating in-place.
    """
    delay = get_delay()

    offset_x = offset
    offset_y = offset_x + length
    file_size = get_file_size(file_input)
    remainder = file_size - offset_y

    if (offset_x > file_size) or (offset_y > file_size):
        return

    fh_input = open(file_input, "r+b")
    while remainder > 0:
        if (remainder < buffer_size):
            buffer_size = remainder

        fh_input.seek(offset_y)
        buffer_input = bytearray(b"" + fh_input.read(buffer_size))
        fh_input.seek(offset_x)
        fh_input.write(buffer_input)

        offset_x += buffer_size
        offset_y += buffer_size
        remainder -= buffer_size
        time.sleep(delay)

    fh_input.truncate(offset_x)
    fh_input.close()

def __validate_files(file_input, file_key, file_output):
    """
        Check if any of the given files already are being processed by another
        Erfr component and, if yes, cancel the process.
    """
    for task in range(1, get_max_tasks() + 1):
        task_file = get_task_file(task)

        if file_exists(task_file):
            fh_task = open(task_file, "r")

            try:
                content = str(base64.b64decode(fh_task.read()))
                list_content = content.split(";")
                for item in list_content:
                    i = item.split(",")

                    if i[1] == file_input or i[1] == file_key or \
                       i[1] == file_output:
                        return task
            except:
                continue
            finally:
                fh_task.close()

    return 0

# EOF

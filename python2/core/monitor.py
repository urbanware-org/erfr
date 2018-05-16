#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# ============================================================================
# Erfr - One-time pad encryption tool
# Monitor core module
# Copyright (C) 2018 by Ralf Kilian
# Distributed under the MIT License (https://opensource.org/licenses/MIT)
#
# Website: http://www.urbanware.org
# GitHub: https://github.com/urbanware-org/erfr
# ============================================================================

__version__ = "4.3.3"

import base64
import common
import os
import paval as pv
import sys
import time

def get_status(task_id, delay=0):
    """
        Get the status of the Erfr process with the given task ID.
    """
    task_file = common.get_task_file(task_id)
    pv.intrange(task_id, "task ID", 1, common.get_max_tasks(), False)
    pv.intvalue(delay, "delay", True, True, False)

    delay = int(delay)
    task_id = int(task_id)
    progress_key = True
    process_type = ""
    process_type_list = ["encryption", "decryption", "key generation"]
    file_input_path = ""
    file_input_size = 0
    file_key_path = ""
    file_key_size = 0
    file_output_path = ""
    file_output_size = 0
    valid_type = False

    if not common.file_exists(task_file):
        common.exception("No process is running with the given task ID.")

    dict_contents = __read_content(task_file)
    process_type = dict_contents["process_type"]
    if process_type == "":
        common.exception("The process type cannot be empty.")

    for item in process_type_list:
        if process_type == item:
            valid_type = True

    if not valid_type:
        common.exception("The process type '%s' is not supported." \
                         % process_type)

    file_input_path = dict_contents["file_input_path"]
    file_input_size = dict_contents["file_input_size"]

    if "crypt" in process_type:
        file_key_path = dict_contents["file_key_path"]
        file_key_size = dict_contents["file_key_size"]
        file_output_path = dict_contents["file_output_path"]
        file_output_size = dict_contents["file_output_size"]
        if process_type == "decryption":
            progress_key = False

    print
    print "Monitoring Erfr %s process with task ID %s." % \
              (process_type, task_id)
    if delay > 0:
        if delay == 1:
            print "Refreshing the process status every second."
        else:
            print "Refreshing the process status every %s seconds." % \
                  str(delay)

    print
    print "-" * 78
    if file_key_path == "" and file_output_path == "":
        __monitor_file(task_file, file_input_path, file_input_size,
                       "File name", delay, True)
    else:
        __monitor_file(task_file, file_input_path, file_input_size,
                       "Input file", delay, False)
        print
        __monitor_file(task_file, file_key_path, file_key_size, "Key file",
                       delay, progress_key)
        print
        __monitor_file(task_file, file_output_path, file_output_size,
                       "Output file", delay, True)
    print "-" * 78
    print

    if delay > 0:
        print "Process finished."

def get_version():
    """
        Return the version of this module.
    """
    return __version__

def __format_size(file_size):
    """
        Format file size information depending on the amount of bytes.
    """
    file_size = int(file_size)
    list_units = ["B", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    list_index = 0

    while file_size > 1000:
        file_size = float(file_size) / 1000
        list_index += 1
        if list_index > len(list_units) - 1:
            list_index = len(list_units) - 1
            break

    if list_index > 0:
       file_size = round(file_size, 1)
       unit = list_units[list_index]
    else:
        if file_size == 1:
            unit = "byte"
        else:
            unit = "bytes"

    return "%s %s" % (str(file_size), unit)

def __monitor_file(task_file, file_path, file_size, description, delay,
                   progress):
    """
        Monitor the file size of the given file.
    """
    file_name = os.path.basename(file_path)
    file_dir = __remove_duplicate_chars( \
        file_path.rstrip(file_name).rstrip(os.path.sep), os.path.sep)
    file_size = int(file_size)

    file_size_init = 0
    file_size_current = 0
    file_size_perc = 0

    chars_running = ["-", "\\", "|", "/"]
    chars_stalled = ["?", " "]
    chars_missing = ["X", " "]
    delay_running = 0.1
    delay_stalled = 0.6

    progress_chars = chars_running
    progress_count = 0
    stalled = False
    wait = delay_running

    display_file_info = \
        bool(int(common.global_config(["KeyGenerator", "Monitor"],
                                      ["display_file_info"], "1")))

    if display_file_info:
        print ("%s:" % description).ljust(16, " ") + file_name
        print ("File path:").ljust(16, " ") + file_dir
    else:
        print "%s" % description

    if file_size < 1000:
        print ("File size:").ljust(16, " ") + ("%s bytes total" % file_size)
    else:
        size_round = __format_size(file_size)
        print ("File size:").ljust(16, " ") + \
              ("%s (%s bytes total)" % (size_round, file_size))

    if not progress:
        return

    try:
        file_size_init = file_size
        file_size_current = common.get_file_size(file_path)
        file_size_perc = int((file_size_current * 100) / file_size)
    except:
        pass

    count = 0
    while file_size_current < file_size:
        try:
            file_size_current = common.get_file_size(file_path)
        except:
            pass

        if file_size_current == file_size:
            break

        file_exists_task = common.file_exists(task_file)
        file_exists_input = common.file_exists(file_path)

        if not file_exists_task or not file_exists_input:
            if not file_exists_input:
                progress_chars = chars_missing
            else:
                progress_chars = chars_stalled
            stalled = True
            wait = delay_stalled
        else:
            progress_chars = chars_running
            wait = delay_running
            if stalled:
                dict_contents = __read_content(task_file)
                if not int(dict_contents["file_input_size"]) == \
                       file_size_init:
                    print "-" * 78
                    common.exception("Task mismatch. Process cancelled.")
                stalled = False

        progress_count += 1
        if progress_count >= len(progress_chars):
            progress_count = 0

        if delay == 0:
            __progress(file_size_perc, None, True)
            return

        if delay > 0:
            if file_size_perc < 100:
                __progress( \
                    file_size_perc, progress_chars[progress_count], False)

                time.sleep(wait)
                if count < delay:
                    count += 0.1
                    continue
                else:
                    count = 0

        try:
            file_size_current = common.get_file_size(file_path)
            if not stalled:
                file_size_perc = int((file_size_current * 100) / file_size)
        except:
            pass

    __progress(100, " ", True)

def __progress(percent, char, newline):
    """
        Print single-lined progress information.
    """
    if char == None:
        char = ""

    status_line = \
        common.progress_bar(78, percent, "Progress:", 16, "=", char, True)
    sys.stdout.write(status_line + "\r")
    sys.stdout.flush()

    if newline:
        print

def __read_content(task_file):
    """
        Read the contents of the task file.
    """
    dict_content = {}
    seperator = "\n"

    fh_task = open(task_file, "rb")
    content = fh_task.read()
    fh_task.close()

    try:
        # Run the appropriate code for the Python framework used
        if sys.version_info[0] == 2:
            temp = base64.decodestring(content)
            list_content = temp.split(seperator)
        elif sys.version_info[0] > 2:
            temp = base64.decodestring(content)
            content = temp.decode(sys.getdefaultencoding())
            list_content = content.split(seperator)
    except:
        list_content = content.split(seperator)

    for item in list_content:
        i = item.split(";", 2)
        if i[0] == "type":
            dict_content.update({"process_type": i[1]})
        if i[0] == "input":
            dict_content.update({"file_input_size": i[1]})
            dict_content.update({"file_input_path": i[2]})
        if i[0] == "key":
            dict_content.update({"file_key_size": i[1]})
            dict_content.update({"file_key_path": i[2]})
        if i[0] == "output":
            dict_content.update({"file_output_size": i[1]})
            dict_content.update({"file_output_path": i[2]})
        if i[0] == "timestamp":
            dict_content.update({"timestamp": i[1]})

    return dict_content

def __remove_duplicate_chars(string_input, string_replace):
    """
        Remove duplicate chars from a string.
    """
    while (string_replace * 2) in string_input:
        string_input = \
            string_input.replace((string_replace * 2), string_replace)

    return string_input

# EOF

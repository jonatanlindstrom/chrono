#!/usr/bin/env python3
# -*- coding: utf-8 -*

import os
import glob
import nose


def check_test_files(directory):
    test_files = glob.glob(os.path.join(directory, 'test_*'))
    error_list = []
    for test_file in test_files:
        if os.access(test_file, os.X_OK):
            error_list.append(test_file)

    if error_list:
        header = 'Please unset the executable flag for the following files:'
        error_list.insert(0, header)
    return error_list


def run_nose(directory):
    os.environ["NOSE_WHERE"] = directory
    os.environ["NOSE_WITH_COVERAGE"] = "1"
    os.environ["NOSE_COVER_PACKAGE"] = "chrono"
    os.environ["NOSE_COVER_BRANCHES"] = "1"
    os.environ["NOSE_COVER_HTML"] = "1"
    os.environ["NOSE_REDNOSE"] = "1"
    os.environ["NOSE_VERBOSE"] = "1"
    return nose.main()


if __name__ == '__main__':
    test_directory = os.path.dirname(os.path.abspath(__file__))
    errors = check_test_files(test_directory)
    if len(errors) == 0:
        exit_code = run_nose(test_directory)
    else:
        exit_code = 1
        for error in errors:
            print(error)
    sys.exit(exit_code)

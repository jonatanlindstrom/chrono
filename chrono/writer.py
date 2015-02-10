# -*- coding: utf-8 -*-
import os
import re

from chrono import errors

def write_line(file_path, string):
    string
    date_match = re.match("^(\d+)\.\s+.*$", string)
    if not date_match:
        raise errors.BadDateError()
    date = date_match.group(1)

    if os.path.exists(file_path):
        with open(file_path, 'r') as text_file:
            lines = text_file.readlines()
        lines = [l.rstrip("\n") for l in lines if l.rstrip()]
    else:
        lines = []

    if lines and lines[-1].startswith(date + "."):
        lines[-1] = string
    else:
        lines.append(string)

    lines = [l + "\n" for l in lines]
    with open(file_path, 'w') as text_file:
        text_file.writelines(lines)

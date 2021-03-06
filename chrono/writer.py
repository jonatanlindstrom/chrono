# -*- coding: utf-8 -*-
import os
import re

from chrono import errors


def write_line(file_path: str, date_string: str):
    file_match = re.match("^[1-2][0-9]{3}-[0-2][0-9]\.txt",
                          os.path.basename(file_path))
    if not file_match:
        raise errors.ReportError(
            "File name is not a month file: \"{}\"".format(file_path))

    date_match = re.match("^\s*(\d+)\.\s+.*$", date_string)
    if not date_match:
        raise errors.ReportError("Bad report string: \"{}\"".format(
            date_string))

    date = date_match.group(1)
    date_string = date_string.strip()

    if os.path.exists(file_path):
        with open(file_path, 'r') as text_file:
            lines = text_file.readlines()
        lines = [l.rstrip("\n") for l in lines if l.rstrip()]
    else:
        lines = []

    if lines and lines[-1].startswith(date + "."):
        lines[-1] = date_string
    else:
        lines.append(date_string)

    lines = "\n".join(lines)
    with open(file_path, 'w') as text_file:
        text_file.write(lines)

# -*- coding: utf-8 -*-


def pretty_timedelta(timedelta, signed=False):
    if timedelta is None:
        return ""

    if signed:
        template = "{:+2d}:{:02}"
    else:
        template = "{}:{:02}"
    seconds = int(timedelta.total_seconds())
    negative = seconds < 0
    hours = abs(seconds) // 3600
    minutes = abs(seconds) // 60 % 60
    if negative:
        hours = -hours
    formated_timedelta = template.format(hours, minutes)
    return formated_timedelta

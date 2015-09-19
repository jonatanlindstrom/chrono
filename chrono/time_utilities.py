# -*- coding: utf-8 -*-

from datetime import timedelta

def pretty_timedelta(timedelta: timedelta, signed: bool = False) -> str:
    """
    :param timedelta:
    :param bool signed:
    :return string:
    """
    if timedelta is None:
        return ""

    seconds = int(timedelta.total_seconds())
    positive = seconds > 0
    negative = seconds < 0
    hours = abs(seconds) // 3600
    minutes = abs(seconds) // 60 % 60

    if positive and signed:
        sign = "+"
    elif negative:
        sign = "-"
    else:
        sign = ""

    formated_timedelta = "{}{}:{:02}".format(sign, hours, minutes)
    return formated_timedelta

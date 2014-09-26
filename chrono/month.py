# -*- coding: utf-8 -*-

import datetime
import re
from chrono import errors
from chrono.day import Day

class Month(object):
    def __init__(self, month_string):
        match = re.match("^(\d{4})-([0-1][0-9])$", month_string)
        if match:
            self.year = match.group(1)
            self.month = match.group(2)
        else:
            raise errors.BadDateError("Bad date string: \"{}\"".format(
                month_string))
        self.days = []
    
    def add_day(self, date_string):
        new_day = Day(date_string)
        for old_day in self.days:
            if not old_day.complete():
                raise errors.ReportError("A new day can't be added until all "
                                         "previous days are complete.")
        self.days.append(new_day)
        return new_day

    def calculate_flextime(self):
        flextime = datetime.timedelta()
        for day in self.days:
            flextime += day.calculate_flextime()
        return flextime

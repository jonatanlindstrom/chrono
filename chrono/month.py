# -*- coding: utf-8 -*-

import datetime
import re
from chrono import errors
from chrono.day import Day

class Month(object):
    def __init__(self, month_string):
        match = re.match("^(\d{4})-([0-1][0-9])$", month_string)
        if match:
            self.year = int(match.group(1))
            self.month = int(match.group(2))
        else:
            raise errors.BadDateError("Bad date string: \"{}\"".format(
                month_string))
        self.days = []
    
    def add_day(self, date_string):
        new_day = Day(date_string)
        if new_day.date.year != self.year or new_day.date.month != self.month:
            raise errors.ReportError("New date string didn't match month. "
                                     "{}-{:02d} doesn't include {}.".format(
                                     self.year, self.month, date_string))

        for old_day in self.days:
            if not old_day.complete():
                raise errors.ReportError("New days can't be added while the "
                                         "report for a previous day is "
                                         "incomplete.")

        if date_string != self.next_workday():
            raise errors.ReportError("New work days must be added "
                                     "consecutively.")

        self.days.append(new_day)
        return new_day

    def complete(self):
        status = (
            not self.next_workday().startswith("{}-{:02d}".format(
                self.year, self.month))
            and self.days[-1].complete())

        return status

    def next_workday(self):
        if len(self.days) == 0:
            next_day = Day("{}-{:02d}-01".format(self.year, self.month))
        else:
            next_day = Day((self.days[-1].date + datetime.timedelta(days=1)).isoformat())
        while next_day.expected_hours <= datetime.timedelta():
            next_day = Day((next_day.date + datetime.timedelta(days=1)).isoformat())
        return next_day.date.isoformat()

    def calculate_flextime(self):
        flextime = datetime.timedelta()
        for day in self.days:
            print("{}: {}".format(day.date.isoformat(), day.calculate_flextime()))
            flextime += day.calculate_flextime()
        return flextime

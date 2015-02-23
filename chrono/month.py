# -*- coding: utf-8 -*-

import datetime
import re

from chrono import errors
from chrono.day import Day, DayType
from chrono.time_utilities import pretty_timedelta


class Month(object):
    def __init__(self, month_string, user=None):
        match = re.match("^(\d{4})-([0-1][0-9])$", month_string)
        if match:
            self.year = int(match.group(1))
            self.month = int(match.group(2))
        else:
            raise errors.BadDateError("Bad date string: \"{}\"".format(
                month_string))
        self.days = []
        self.holidays = {}
        self.user = user

    def add_day(self, date_string):
        new_day = Day(date_string)
        if new_day.date.year != self.year or new_day.date.month != self.month:
            raise errors.ReportError("New date string didn't match month. "
                                     "{}-{:02d} doesn't include {}.".format(
                                         self.year, self.month, date_string))

        for old_day in self.days:
            if new_day.date == old_day.date:
                raise errors.ReportError(
                    "Date 2014-09-02 already added to month.")
            if not old_day.complete():
                raise errors.ReportError("New days can't be added while the "
                                         "report for a previous day is "
                                         "incomplete.")

        next_workday = datetime.datetime.strptime(
            self.next_workday(), "%Y-%m-%d").date()

        if new_day.date > next_workday:
            raise errors.ReportError(
                "New work days must be added consecutively. Expected {}, got "
                "{}.".format(self.next_workday(), date_string))

        if date_string in self.holidays:
            new_day.day_type = DayType.holiday
            new_day.info = self.holidays[date_string]
        self.days.append(new_day)
        return new_day

    def complete(self):
        date_string = "{}-{:02d}".format(self.year, self.month)
        return (not self.next_workday().startswith(date_string) and
                self.days[-1].complete())

    def next_workday(self):
        if len(self.days) == 0:
            next_day = Day("{}-{:02d}-01".format(self.year, self.month))
        else:
            next_day = Day((self.days[-1].date +
                            datetime.timedelta(days=1)).isoformat())

        while (next_day.day_type != DayType.working_day or
               next_day.date.isoformat() in self.holidays):
            next_day = Day((next_day.date +
                            datetime.timedelta(days=1)).isoformat())

        return next_day.date.isoformat()

    def next_month(self):
        next_year = self.year
        next_month = self.month + 1
        if next_month > 12:
            next_month = 1
            next_year += 1
        return "{}-{:02d}".format(next_year, next_month)

    def calculate_flextime(self):
        flextime = datetime.timedelta()
        for day in self.days:
            flextime += day.calculate_flextime()
        return flextime

    def add_holiday(self, date_string, name):
        self.holidays[date_string] = name
        for day in self.days:
            if day.date.isoformat() == date_string:
                day.day_type = DayType.holiday
                day.info = name

    def used_vacation(self, date_string=None):
        if date_string is not None:
            date = datetime.datetime.strptime(date_string, "%Y-%m-%d").date()
            vacation_days = [day for day in self.days
                             if day.day_type == DayType.vacation
                             and day.date <= date]
        else:
            vacation_days = [day for day in self.days
                             if day.day_type == DayType.vacation]

        return len(vacation_days)

    def sick_days(self):
        return len([day for day in self.days
                    if day.day_type == DayType.sick_day])

    def __str__(self):
        width = 40
        month_string = "{month.year}-{month.month:02} - {name}".format(
            month=self,
            name=datetime.datetime(self.year, self.month, 1).strftime("%B"))

        string = "\n{:^{width}}".format(month_string, width=width)
        string += "\n{}\n".format("-" * width)
        string += "\n".join(day.list_str() for day in self.days)
        string += "\n{}".format("-" * width)
        string += "\n{:>{width}}\n".format(
            pretty_timedelta(self.calculate_flextime(), signed=True),
            width=width)
        return string
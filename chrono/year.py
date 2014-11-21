# -*- coding: utf-8 -*-

import datetime
import re
from chrono import month
from chrono import day
from chrono import errors


class Year(object):
    def __init__(self, year_string, flextime=None, start_date=None):
        if not isinstance(year_string, str):
            raise errors.BadDateError(
                "Argument year_string must be a string, was \"{}\".".format(
                    type(year_string).__name__))

        year_match = re.match("(\d{4})", year_string)
        if not year_match:
            raise errors.BadDateError(
                "Argument year_string must be a year (e.g. \"YYYY\"), was "
                "\"{}\".".format(year_string))

        if flextime is not None and not isinstance(flextime,
                                                   datetime.timedelta):
            raise errors.BadDateError(
                "Argument flextime must be a timedelta object, was \"{}\"."
                .format(type(flextime).__name__))

        if start_date is not None and not isinstance(start_date, str):
            raise errors.BadDateError(
                "Argument start_date must be a string, was \"{}\".".format(
                    type(start_date).__name__))

        if start_date is not None and not re.match("\d{4}-\d{2}", start_date):
            raise errors.BadDateError(
                "Argument start_date must be a ISO date string (e.g. "
                "\"YYYY-MM-DD\", was \"{}\".".format(start_date))

        self.year = int(year_string)
        self.months = []
        self.flextime = flextime or datetime.timedelta()
        self.force_start_date = start_date
        self.holidays = {"{}-{:02d}".format(self.year, m): {}
                         for m in range(1, 13)}

    def complete(self):
        return (not self.next_workday().startswith("{}-".format(self.year)) and
                self.months[-1].complete())

    def next_workday(self):
        if len(self.months) == 0:
            if self.force_start_date is None:
                tmp_month_string = "{}-01".format(self.year)
            else:
                tmp_month_string = self.force_start_date[:7]
            tmp_month = month.Month(tmp_month_string)
            month_holidays = self.holidays[tmp_month_string].items()
            for date_string, holiday in month_holidays:
                tmp_month.add_holiday(date_string, holiday)
            next_workday = tmp_month.next_workday()
        else:
            next_workday = self.months[-1].next_workday()
        return next_workday

    def next_month(self):
        if len(self.months) == 0:
            if self.force_start_date is None:
                next_month = "{}-01".format(self.year)
            else:
                next_month = self.force_start_date[:7]
        else:
            next_month = self.months[-1].next_month()
        return next_month

    def next_year(self):
        return str(self.year + 1)

    def calculate_flextime(self):
        flextime = self.flextime
        for month in self.months:
            flextime += month.calculate_flextime()
        return flextime

    def sick_days(self):
        sick_days = 0
        for month in self.months:
            sick_days += month.sick_days()
        return sick_days

    def used_vacation(self, date_string=None):
        used_vacation = 0
        for month in self.months:
            used_vacation += month.used_vacation(date_string=date_string)
        return used_vacation

    def add_day(self, date_string):
        new_day = day.Day(date_string)
        if new_day.date.year != self.year:
            raise errors.ReportError(
                "New date string didn't match year. {} doesn't include {}."
                .format(self.year, date_string))

        if self.next_workday()[:7] == self.next_month():
            new_month = month.Month(self.next_month())
            for date, name in self.holidays[self.next_month()].items():
                new_month.add_holiday(date, name)
            self.months.append(new_month)
        day_1 = self.months[-1].add_day(date_string)
        return day_1

    def add_holiday(self, date_string, name):
        date = datetime.datetime.strptime(date_string, "%Y-%m-%d").date()
        self.holidays[date_string[:7]][date_string] = name
        for month in self.months:
            if date.month == month.month:
                month.add_holiday(date_string, name)

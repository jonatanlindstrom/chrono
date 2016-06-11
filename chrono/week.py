# -*- coding: utf-8 -*-

import datetime

import isoweek

from chrono import day
from chrono import errors
from chrono.time_utilities import pretty_timedelta


class Week:
    def __init__(self, year, week_number):
        self._week = isoweek.Week(year, week_number)
        self.number = week_number
        self.year = year
        self.monday = day.Day(self._week.monday().isoformat())
        self.tuesday = day.Day(self._week.tuesday().isoformat())
        self.wednesday = day.Day(self._week.wednesday().isoformat())
        self.thursday = day.Day(self._week.thursday().isoformat())
        self.friday = day.Day(self._week.friday().isoformat())
        self.saturday = day.Day(self._week.saturday().isoformat())
        self.sunday = day.Day(self._week.sunday().isoformat())

    @classmethod
    def from_days(cls, *args):
        """Create a Week object from a set of Day objects.
        :type args (day.Day):
        """
        dates = []
        week = None

        for arg in args:
            if week is None:
                week = arg.date.isocalendar()[:2]
            elif week != arg.date.isocalendar()[:2]:
                raise errors.BadDateError(
                    "All added days doesn't belong to the same week.")

            if arg.date in dates:
                raise errors.BadDateError(
                    "The same date ({}) was added multiple times to week."
                    .format(arg.date.isoformat()))
            dates.append(arg.date)
        tmp_week = cls(*week)

        for tmp_day in args:
            if tmp_day.date.weekday() == 0:
                tmp_week.monday = tmp_day
            elif tmp_day.date.weekday() == 1:
                tmp_week.tuesday = tmp_day
            elif tmp_day.date.weekday() == 2:
                tmp_week.wednesday = tmp_day
            elif tmp_day.date.weekday() == 3:
                tmp_week.thursday = tmp_day
            elif tmp_day.date.weekday() == 4:
                tmp_week.friday = tmp_day
            elif tmp_day.date.weekday() == 5:
                tmp_week.saturday = tmp_day
            elif tmp_day.date.weekday() == 6:
                tmp_week.sunday = tmp_day
        return tmp_week

    @property
    def days(self):
        return [self.monday, self.tuesday, self.wednesday, self.thursday, self.friday, self.saturday, self.sunday]

    def calculate_flextime(self):
        flextime = datetime.timedelta()
        for weekday in (self.monday, self.tuesday, self.wednesday,
                        self.thursday, self.friday, self.saturday,
                        self.sunday):
            flextime += weekday.calculate_flextime()
        return flextime

    def __str__(self):
        width = 40
        week_string = "{}: {} - {}".format(
            self.number,
            self.monday.date.isoformat(),
            self.sunday.date.isoformat())
        string = "\n{:^{width}}".format(week_string, width=width)
        string += "\n{}\n".format("-" * width)
        string += "\n".join(weekday.list_str() for weekday in (
            self.monday, self.tuesday, self.wednesday, self.thursday,
            self.friday, self.saturday, self.sunday))

        string += "\n{}".format("-" * width)
        string += "\n{:>{width}}\n".format(
            pretty_timedelta(self.calculate_flextime(), signed=True),
            width=width)
        return string

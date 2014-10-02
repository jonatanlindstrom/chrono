# -*- coding: utf-8 -*-

import datetime
import re
from enum import Enum
from chrono import errors


class DayType(Enum):
    working_day = 1
    weekend = 2
    holiday = 3
    vacation = 4
    sick_day = 5


class Day(object):
    def __init__(self, date_string):
        try:
            self.date = datetime.datetime.strptime(
                date_string, "%Y-%m-%d").date()

        except ValueError:
            raise errors.BadDateError("Bad date string: \"{}\"".format(
                date_string))
        except TypeError:
            raise TypeError("Given date must be a string.")

        self.start_time = None
        self.lunch_duration = None
        self.end_time = None

        if self.date.isoweekday() < 6:
            self.day_type = DayType.working_day
        else:
            self.day_type = DayType.weekend

    def report_start_time(self, start_time):
        if self.start_time is not None:
            raise errors.ReportError("Date {} allready has a start time."
                                     .format(self.date.isoformat()))

        try:
            start_time = datetime.datetime.strptime(
                start_time, "%H:%M").time()
        except ValueError:
            raise errors.BadTimeError(
                "Bad start time: \"{}\".".format(start_time))

        self.start_time = datetime.datetime.combine(self.date, start_time)

    def report_lunch_duration(self, lunch_duration):
        if self.start_time is None:
            raise errors.ReportError(
                "Date {} must have a start time before a lunch duration can "
                "be reported.".format(self.date.isoformat()))

        if self.lunch_duration is not None:
            raise errors.ReportError("Date {} allready has a lunch duration."
                                     .format(self.date.isoformat()))

        match = re.match("(\d+):([0-5][0-9])", lunch_duration)
        if match:
            self.lunch_duration = datetime.timedelta(
                hours=int(match.group(1)), minutes=int(match.group(2)))

    def report_end_time(self, end_time):
        if self.start_time is None:
            raise errors.ReportError(
                "Date {} must have a start time before an end time can be "
                "reported.".format(self.date.isoformat()))

        if self.lunch_duration is None:
            raise errors.ReportError(
                "Date {} must have a lunch duration before an end time can be "
                "reported.".format(self.date.isoformat()))

        try:
            end_time = datetime.datetime.strptime(
                end_time, "%H:%M").time()

        except TypeError:
            raise TypeError("Given end time must be a string.")
        except ValueError:
            raise errors.BadTimeError("Bad end time: \"{}\"".format(end_time))
        self.end_time = datetime.datetime.combine(self.date, end_time)

    def report(self, start, lunch, end):
        self.report_start_time(start)
        self.report_lunch_duration(lunch)
        self.report_end_time(end)

    def complete(self):
        complete_status = (self.day_type != DayType.working_day or
                           self.start_time is not None and
                           self.lunch_duration is not None and
                           self.end_time is not None)

        return complete_status

    def expected_hours(self):
        if self.day_type == DayType.working_day:
            expected_hours = datetime.timedelta(hours=8)
        else:
            expected_hours = datetime.timedelta(hours=0)
        return expected_hours

    def worked_hours(self):
        if (self.start_time is None or self.lunch_duration is None or
                self.end_time is None):
            raise errors.ReportError("Date {} must have a start time, a lunch "
                                     "duration and an end time before the day "
                                     "can be summarized.".format(
                                         self.date.isoformat()))
        return self.end_time - self.start_time - self.lunch_duration

    def calculate_flextime(self):
        return self.worked_hours() - self.expected_hours()

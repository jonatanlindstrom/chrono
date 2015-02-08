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
        self.comment = None
        self.info = None
        self.deviation = datetime.timedelta()

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

        match = re.match("^(\d{1,2})(?::(\d{2}))?$", lunch_duration)
        if match:
            self.lunch_duration = datetime.timedelta(
                hours=int(match.group(1)), minutes=int(match.group(2) or 0))
        else:
            raise errors.ReportError(
                "Bad lunch duration for date {}: '{}'".format(self.date,
                                                              lunch_duration))

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

    def report_deviation(self, deviation):
        match = re.match("^(\d{1,2})(?::(\d{2}))?$", deviation)
        if match:
            self.deviation = datetime.timedelta(
                hours=int(match.group(1)), minutes=int(match.group(2) or 0))
        else:
            raise errors.ReportError("Bad deviation for date {}: '{}'".format(
                self.date, deviation))

    def report(self, start, lunch, end):
        self.report_start_time(start)
        self.report_lunch_duration(lunch)
        self.report_end_time(end)

    def set_type(self, day_type):
        self.day_type = day_type

    def complete(self):
        complete_status = (self.day_type != DayType.working_day or
                           self.start_time is not None and
                           self.lunch_duration is not None and
                           self.end_time is not None)

        return complete_status

    def expected_hours(self):
        standard_day = 8
        if self.day_type == DayType.working_day:
            expected_hours = datetime.timedelta(hours=standard_day)
        else:
            expected_hours = datetime.timedelta(hours=0)
        return expected_hours

    def worked_hours(self, end_time=None):
        """Calculate worked hours for a working day.
        :type end_time datetime.datetime:  If the day has no end time, a custom
                                           end time can be supplied.
        :rtype: datetime.timedelta
        :raises: errors.ChronoError
        """
        if end_time is None:
            if (self.start_time is None or self.lunch_duration is None or
                    self.end_time is None):
                total_hours = datetime.timedelta()
            else:
                total_hours = self.end_time - self.start_time
                total_hours -= self.lunch_duration
                total_hours -= self.deviation
        else:
            if self.start_time is None or self.complete():
                raise errors.ChronoError("Custom end times can only be tried "
                                         "on days in progress.")
            else:
                total_hours = end_time - self.start_time
                total_hours -= (self.lunch_duration or datetime.timedelta())
                total_hours -= self.deviation
        return total_hours

    def calculate_flextime(self):
        if self.complete():
            flextime = self.worked_hours() - self.expected_hours()
        else:
            flextime = datetime.timedelta()
        return flextime

    def get_info(self):
        info = self.info
        if info:
            info = info.strip()
            info = info.strip()
            info = re.sub("\s+", " ", info)
            self.info = info
        if self.comment:
            self.comment = self.comment.strip()
            self.comment = self.comment.strip()
            self.comment = re.sub("\s+", " ", self.comment)
            if self.comment[-1] not in ".?!":
                self.comment += "."

        if info and self.comment:
            if info[-1] not in ".?!":
                info += "."
        combined = " ".join([text for text in (info, self.comment) if text])
        return combined

    def __str__(self):
        width_label = 20
        width_value = 17
        value = "{day.date} - {}".format(self.date.strftime("%A"), day=self)
        string = """\n{:^{width}}\n""".format(
            value, width=width_label + width_value)

        if self.day_type == DayType.working_day:
            string += "-" * (width_label + width_value)
            string += "\n{:<{width}}".format("Start time:", width=width_label)
            if self.start_time:
                value = self.start_time.strftime("%H:%M")
                string += "{:>{width}}".format(value, width=width_value)

            string += "\n{:<{width}}".format("Lunch:", width=width_label)
            if self.lunch_duration:
                value = "{:}:{:02}".format(
                    int(self.lunch_duration.total_seconds() // 3600),
                    int(self.lunch_duration.total_seconds() % 3600 // 60))

                string += "{:>{width}}".format(value, width=width_value)

            string += "\n{:<{width}}".format("Deviation:", width=width_label)
            if self.deviation > datetime.timedelta():
                value = "{:}:{:02}".format(
                    int(self.lunch_duration.total_seconds() // 3600),
                    int(self.lunch_duration.total_seconds() % 3600 // 60))

                string += "{:>{width}}".format(value, width=width_value)

            string += "\n{:<{width}}".format("End time:", width=width_label)
            if self.end_time:
                value = self.end_time.strftime("%H:%M")
                string += "{:>{width}}".format(value, width=width_value)
            string += "\n{}".format("-" * (width_label + width_value))
            string += "\n{:<{width}}".format(
                "Worked hours:", width=width_label)

            if self.complete():
                worked_hours = self.worked_hours()
            else:
                worked_hours = self.worked_hours(
                    end_time=datetime.datetime.now())

            value = "{:}:{:02}".format(
                int(worked_hours.total_seconds() // 3600),
                int(worked_hours.total_seconds() % 3600 // 60))

            string += "{:>{width}}".format(value, width=width_value)
            if not self.complete():
                string += " ..."
            string += "\n"
        if self.info or self.comment:
            string += "\n{}\n".format(self.get_info())

        return string

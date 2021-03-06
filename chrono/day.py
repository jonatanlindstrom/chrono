# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from enum import Enum
import re
from typing import Optional

from chrono import errors
from chrono.time_utilities import pretty_timedelta


STANDARD_HOURS = 8


class DayType(Enum):
    working_day = 1
    weekend = 2
    holiday = 3
    vacation = 4
    sick_day = 5

    
class Day(object):
    def __init__(self, date_string: str):
        try:
            self.date = datetime.strptime(
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
        self.deviation = timedelta()

        if self.date.isoweekday() < 6:
            self.day_type = DayType.working_day
        else:
            self.day_type = DayType.weekend

    def report_start_time(self, start_time: str):
        if self.start_time is not None:
            raise errors.ReportError("Date {} allready has a start time."
                                     .format(self.date.isoformat()))

        try:
            start_time = datetime.strptime(
                start_time, "%H:%M").time()
        except ValueError:
            raise errors.BadTimeError(
                "Bad start time: \"{}\".".format(start_time))

        self.start_time = datetime.combine(self.date, start_time)

    def report_lunch_duration(self, lunch_duration: str):
        if self.start_time is None:
            raise errors.ReportError(
                "Date {} must have a start time before a lunch duration can "
                "be reported.".format(self.date.isoformat()))

        if self.lunch_duration is not None:
            raise errors.ReportError("Date {} allready has a lunch duration."
                                     .format(self.date.isoformat()))

        match = re.match("^(\d{1,2})(?::(\d{2}))?$", lunch_duration)
        if match:
            self.lunch_duration = timedelta(
                hours=int(match.group(1)), minutes=int(match.group(2) or 0))
        else:
            raise errors.ReportError(
                "Bad lunch duration for date {}: '{}'".format(self.date,
                                                              lunch_duration))

    def report_end_time(self, end_time: str):
        if self.start_time is None:
            raise errors.ReportError(
                "Date {} must have a start time before an end time can be "
                "reported.".format(self.date.isoformat()))

        if self.lunch_duration is None:
            raise errors.ReportError(
                "Date {} must have a lunch duration before an end time can be "
                "reported.".format(self.date.isoformat()))

        try:
            end_time = datetime.strptime(
                end_time, "%H:%M").time()

        except TypeError:
            raise TypeError("Given end time must be a string.")
        except ValueError:
            raise errors.BadTimeError("Bad end time: \"{}\"".format(end_time))
        self.end_time = datetime.combine(self.date, end_time)

    def report_deviation(self, deviation: str):
        match = re.match("^(\d{1,2})(?::(\d{2}))?$", deviation)
        if match:
            self.deviation = timedelta(
                hours=int(match.group(1)), minutes=int(match.group(2) or 0))
        else:
            raise errors.ReportError("Bad deviation for date {}: '{}'".format(
                self.date, deviation))

    def report(self, start: str, lunch: str, end: str):
        self.report_start_time(start)
        self.report_lunch_duration(lunch)
        self.report_end_time(end)

    def set_type(self, day_type: DayType):
        self.day_type = day_type

    def complete(self) -> bool:
        complete_status = (self.day_type != DayType.working_day or
                           self.start_time is not None and
                           self.lunch_duration is not None and
                           self.end_time is not None)

        return complete_status

    def expected_hours(self) -> timedelta:
        if self.day_type == DayType.working_day:
            expected_hours = timedelta(hours=STANDARD_HOURS)
        else:
            expected_hours = timedelta(hours=0)
        return expected_hours

    def worked_hours(self, end_time: Optional[datetime] = None) -> timedelta:
        """Calculate worked hours for a working day.
        :param end_time:  If the day has no end time, a custom end time can be
                          supplied.
        :raises: errors.ChronoError
        """
        if end_time is None:
            if (self.start_time is None or self.lunch_duration is None or
                    self.end_time is None):
                total_hours = timedelta()
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
                total_hours -= (self.lunch_duration or timedelta())
                total_hours -= self.deviation
        return total_hours

    def calculate_flextime(self) -> timedelta:
        if self.complete():
            flextime = self.worked_hours() - self.expected_hours()
        else:
            flextime = timedelta()
        return flextime

    def get_info(self) -> str:
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

    def export(self) -> str:
        string = "{:>2}.".format(self.date.day)
        if self.start_time:
            string += " {}:{}".format(
                self.start_time.hour, self.start_time.strftime('%M'))

        if self.lunch_duration:
            string += " {}".format(pretty_timedelta(self.lunch_duration))
        if self.deviation:
            string += " {}".format(
                pretty_timedelta(self.deviation, signed=True))

        if self.end_time:
            string += " {}".format(self.end_time.strftime('%H:%M'))
        if self.comment:
            string += " {}".format(self.comment)
        return string

    def list_str(self) -> str:
        string = "{:<4}{:>2}.".format(self.date.strftime("%a"),
                                      self.date.day)
        if self.day_type == DayType.working_day:
            string += "{:>7}{:>6}{:>7}{:>6}{:>7}  {}".format(
                self.start_time.strftime("%H:%M") if self.start_time else "",
                pretty_timedelta(self.lunch_duration),
                self.end_time.strftime("%H:%M") if self.end_time else "",
                pretty_timedelta(self.deviation) if self.deviation else "",
                pretty_timedelta(self.calculate_flextime(), signed=True)
                if self.end_time else "",
                self.get_info())
        elif self.day_type == DayType.weekend:
            string += "                  {}".format(self.get_info())
        elif self.day_type == DayType.vacation:
            string += "  Vacation        {}".format(self.get_info())
        elif self.day_type == DayType.holiday:
            string += "                  {}".format(self.get_info())
        elif self.day_type == DayType.sick_day:
            string += "  Sickday         {}".format(self.get_info())

        return string.strip()

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
                value = pretty_timedelta(self.lunch_duration)
                string += "{:>{width}}".format(value, width=width_value)

            string += "\n{:<{width}}".format("Deviation:", width=width_label)
            if self.deviation > timedelta():
                value = pretty_timedelta(self.deviation)
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
                    end_time=datetime.now())

            value = pretty_timedelta(worked_hours)

            string += "{:>{width}}".format(value, width=width_value)
            if not self.complete():
                string += " ..."
            string += "\n"
        if self.info or self.comment:
            string += "\n{}\n".format(self.get_info())

        return string

    def __lt__(self, other):
        return self.date < other.date

    def __gt__(self, other):
        return self.date > other.date

    def __le__(self, other):
        return self.date <= other.date

    def __ge__(self, other):
        return self.date >= other.date

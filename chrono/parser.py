# -*- coding: utf-8 -*-

import re
import os
from chrono.day import DayType
from chrono.month import Month
from chrono.year import Year
from chrono.archive import Archive
from chrono.user import User
from chrono.errors import ParseError


class Parser(object):
    user = None

    def parse_month_file(self, file_name):
        month, _ = os.path.splitext(os.path.basename(file_name))
        with open(file_name, "r") as month_file:
            string = month_file.read()
        parsed_month = self.parse_month_string(string, month)
        return parsed_month

    def parse_month_string(self, string, month):
        parsed_month = Month(month)
        empty_pattern = re.compile("^\s*$")
        date_pattern = re.compile("^(\d{1,2})\.$")
        time_pattern = re.compile("^(\d{1,2}:\d{2})$")
        hour_pattern = re.compile("^(\d{1,2})$")
        sick_pattern = re.compile("^[Ss]$")
        vacation_pattern = re.compile("^[Vv]$")
        comment_pattern = re.compile("([\"\'].*[\"\'])\s*$")

        for line in string.split("\n"):
            if empty_pattern.match(line):
                continue
            match = comment_pattern.search(line)
            if match:
                comment = match.group(1)

                # remove comment
                line = comment_pattern.sub("", line)
            else:
                comment = None
            line_tokens = line.split()
            token = line_tokens.pop(0)
            day_match = date_pattern.match(token)
            if day_match:
                if self.user is None:
                    parsed_day = parsed_month.add_day(
                        "{m.year}-{m.month:02d}-{0:02d}".format(
                            int(day_match.group(1)), m=parsed_month))
                else:
                    parsed_day = self.user.add_day(
                        "{m.year}-{m.month:02d}-{0:02d}".format(
                            int(day_match.group(1)), m=parsed_month))
            else:
                raise ParseError(
                    "Could not parse date in {m.year}-{m.month:02}: \"{}\""
                    .format(token, m=parsed_month))
            while line_tokens:
                token = line_tokens.pop(0)
                if sick_pattern.match(token):
                    parsed_day.set_type(DayType.sick_day)
                elif vacation_pattern.match(token):
                    parsed_day.set_type(DayType.vacation)
                else:
                    hour_match = hour_pattern.match(token)
                    time_match = time_pattern.match(token)
                    if hour_match:
                        hours = hour_match.group(1)
                        if parsed_day.start_time is None:
                            raise ParseError(
                                "Could not parse start time for date {}. Time "
                                "must be given in hours and minutes, got "
                                "\"{}\".".format(parsed_day.date, hours))

                        elif parsed_day.lunch_duration is None:
                            parsed_day.report_lunch_duration(hours)
                        elif parsed_day.end_time is None:
                            raise ParseError(
                                "End time must be given with hours and "
                                "minutes, was '{}'.".format(hours))
                        else:
                            parsed_day.report_deviation(hours)
                    elif time_match:
                        time = time_match.group(1)
                        if parsed_day.start_time is None:
                            parsed_day.report_start_time(time)
                        elif parsed_day.lunch_duration is None:
                            parsed_day.report_lunch_duration(time)
                        elif parsed_day.end_time is None:
                            parsed_day.report_end_time(time)
                        else:
                            parsed_day.report_deviation(time)
                    else:
                        if parsed_day.start_time is None:
                            raise ParseError(
                                "Could not parse start time for date "
                                "{}: \"{}\"".format(parsed_day.date, token))

                        elif parsed_day.lunch_duration is None:
                            raise ParseError(
                                "Could not parse lunch duration for date "
                                "{}: \"{}\"".format(parsed_day.date, token))
                        elif parsed_day.end_time is None:
                            raise ParseError(
                                "Could not parse end time for date "
                                "{}: \"{}\"".format(parsed_day.date, token))
                        else:
                            raise ParseError(
                                "Could not parse deviation for date "
                                "{}: \"{}\"".format(parsed_day.date, token))

                if comment:
                    if comment[0] != comment[-1]:
                        raise ParseError(
                            "No endquote in comment for date {}.".format(
                                parsed_day.date.isoformat()))

                    parsed_day.comment = comment.strip("\"\'")
        if self.user is None:
            return parsed_month
        else:
            return self.user.years[-1].months[-1]

    def parse_archive_file(self, file_name):
        parsed_archive = Archive()
        with open(file_name, "r") as month_file:
            archive_string = month_file.read()
        month_pattern = re.compile("^([0-9]{4}-[01][0-9])\n",
                                   flags=re.MULTILINE)

        month_tokens = [string for string in
                        month_pattern.split(archive_string) if string]

        month_tokens = zip(*(iter(month_tokens),) * 2)
        for month, month_string in month_tokens:
            parsed_month = self.parse_month_string(month_string, month)
            parsed_archive.archive_month(parsed_month)
        return parsed_archive

    def parse_year_file(self, file_name):
        year = os.path.splitext(os.path.basename(file_name))[0]
        if self.user is not None:
            if self.user.employed_date.year == int(year):
                parsed_year = Year(
                    year, start_date=self.user.employed_date.isoformat())

            elif len(self.user.years) == 0:
                raise Exception
            else:
                parsed_year = Year(year)
        else:
            parsed_year = Year(year)
        with open(file_name, "r") as year_file:
            year_string = year_file.read()

        holiday_pattern = re.compile(
            "^\s*(\d{4}-\d{2}-\d{2})\s*:\s+([\"\'].*[\"\'])\s*$",
            flags=re.MULTILINE)

        comment_pattern = re.compile("#.*$", flags=re.MULTILINE)

        year_string = comment_pattern.sub("", year_string)
        holidays = holiday_pattern.findall(year_string)
        for date, name in holidays:
            name = name.strip("\"\'")
            parsed_year.add_holiday(date, name)
        if self.user is not None:
            self.user.add_year(parsed_year)
        return parsed_year

    def parse_user_file(self, file_name):
        
        with open(file_name, "r") as user_file:
            user_string = user_file.read()
        name_pattern = re.compile(
            "^\s*[Nn]ame\s*:\s*(\w+\s\w+)\s*$", flags=re.MULTILINE)
        
        employment_pattern = re.compile(
            "^\s*[Ee]mployment\s*:\s*(\d+)\s*%\s*$", flags=re.MULTILINE)
        
        payed_vacation_pattern = re.compile(
            "^\s*[Pp]ayed\s*[Vv]acation\s*:\s*(\d+)\s*$", flags=re.MULTILINE)
        
        vacation_month_pattern = re.compile(
            "^\s*[Vv]acation\s*[Mm]onth\s*:\s*(\d+)\s*$", flags=re.MULTILINE)
        
        employed_date_pattern = re.compile(
            "^\s*[Ee]mployed\s*[Dd]ate\s*:\s*(\d{4}-\d{2}-\d{2})\s*$",
            flags=re.MULTILINE)

        extra_vacation_pattern = re.compile(
            "^\s*[Ee]xtra\s*[Vv]acation\s*:\s*(\d+)\s*$",
            flags=re.MULTILINE)
        
        name_match = name_pattern.search(user_string)
        employment_match = employment_pattern.search(user_string)
        payed_vacation_match = payed_vacation_pattern.search(user_string)
        vacation_month_match = vacation_month_pattern.search(user_string)
        employed_date_match = employed_date_pattern.search(user_string)
        extra_vacation_match = extra_vacation_pattern.search(user_string)
        
        if employed_date_match:
            employed_date = employed_date_match.group(1)
            parsed_user = User(employed_date=employed_date)
        else:
            parsed_user = User()

        if name_match:
            parsed_user.name = name_match.group(1)
        if employment_match:
            parsed_user.employment = int(employment_match.group(1))
        if payed_vacation_match:
            parsed_user.payed_vacation = int(payed_vacation_match.group(1))
        if vacation_month_match:
            parsed_user.vacation_month = int(vacation_month_match.group(1))
        if extra_vacation_match:
            parsed_user.extra_vacation = int(extra_vacation_match.group(1))

        self.user = parsed_user
        return self.user

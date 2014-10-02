# -*- coding: utf-8 -*-

import datetime
import re
import os
from chrono.day import DayType
from chrono.month import Month


class Parser(object):
    def parse_month_file(self, file_name):
        month_string, _ = os.path.splitext(os.path.basename(file_name))
        parsed_month = Month(month_string)

        with open(file_name, "r") as month_file:
            month_string = [line for line in month_file]
        day_pattern = re.compile(
            "^(\d{1,2})\.(?:\s+(?:[Ss]|[Vv]|(\d{1,2}:\d{2})(?:\s+(\d+:\d{2})"
            "(?:\s+(\d{1,2}:\d{2}))?)?))?$")
        for line in month_string:
            match = day_pattern.match(line)
            if match:
                day, start_time, lunch_duration, end_time = match.groups()
                parsed_day = parsed_month.add_day(
                    "{m.year}-{m.month:02d}-{0:02d}".format(int(day),
                                                            m=parsed_month))

                if "S" in line:
                    parsed_day.day_type = DayType.sick_day
                elif "V" in line:
                    parsed_day.day_type = DayType.vacation
                if start_time:
                    parsed_day.report_start_time(start_time)
                if lunch_duration:
                    parsed_day.report_lunch_duration(lunch_duration)
                if end_time:
                    parsed_day.report_end_time(end_time)
                print(parsed_day.day_type)
        return parsed_month

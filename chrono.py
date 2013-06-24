#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Usage: chrono.py [-c] ( ls | setup | edit [<month>]) 
       chrono.py [-c] report <report_string>
       chrono.py -h | --help

The magical chrono time report tool.

Arguments:
  ls            List reports
  setup         Set up work info
  report        Make new report
  report_string A report string
  edit          Edit a report in external editor

Options:
  -h --help                    Print this message.
  -c --color                   Prints whith color
"""

from docopt import docopt
import logging
import os
import calendar as cal
import datetime
import re
import glob
import subprocess
import sys

def main():
    arguments = docopt(__doc__)
    chrono = Chrono()
    print arguments
    if arguments['--color']:
        chrono.settings['color'] = True
    
    if arguments['ls']:
        chrono.make_reports()
    elif arguments['report']:
        chrono.new_report(arguments["<report_string>"]) 
    elif arguments['edit']:
        chrono.edit_report(arguments['<month>'])
    elif arguments['setup']:
        chrono.setup()

class Chrono(object):
    
    def __init__(self):
        if not os.path.isfile(os.path.expanduser("~/.chrono")):
            settings = {}
            settings["chronopath"] = os.path.expanduser("~/chrono/")
            self.write_dot_file(settings)
        self.settings = self.read_dot_file()

        self.user = self.create_user()
        self.months = []
        self.calendar = {}
        self.report_archive = Archive()
        
        self.read_year_conf()
        self.read_report_files()
        
    def write_dot_file(self, settings):
        dot_file = open(os.path.expanduser("~/.chrono.tmp"), "w")
        for key, value in settings.iteritems():
            dot_file.write("%s: %s\n" % (key, value))
        dot_file.close()
        os.rename(os.path.expanduser("~/.chrono.tmp"), os.path.expanduser("~/.chrono"))
    
    def read_dot_file(self):
        settings = {}
        raw_settings = open(os.path.expanduser("~/.chrono"), "r")
        for line in raw_settings.readlines():
            delimiter_pos = line.find(":")
            key = line[0:delimiter_pos].strip()
            value = line[delimiter_pos + 1:].strip()
            
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            
            settings[key] = value
        return settings
    
    def read_year_conf(self):
        months = ["JANUARY", "FEBRUARY", "MARCH", "APRIL",
                  "MAY", "JUNE", "JULY",
                  "AUGUST", "SEPTEMBER",
                  "OCTOBER", "NOVEMBER", "DECEMBER"]
        year_files = glob.glob(os.path.join(self.settings["chronopath"], "20[0-9][0-9].conf"))
        for year_file in year_files:
            year = int(os.path.splitext(os.path.split(year_file)[1])[0])
            self.calendar[year] = {}

            month = None
            f = open(year_file, "r")
            for line in f.readlines():
                # Parse comment which is only allowed last
                m = _comment_pattern.search(line)
                if m:
                    if m.group(2):
                        comment = m.group(2)
                    elif m.group(5):
                        comment = m.group(5)
                    line = _comment_pattern.sub(' ', line)
                else:
                    comment = ""
                                
                tokens = line.strip().split()
                if len(tokens) == 1 and tokens[0].upper() in months:
                    month = months.index(tokens[0].upper()) + 1
                    self.calendar[year][month] = {}
                elif month and tokens:

                    # Parse date
                    if tokens[0].find(".") == -1:
                        raise Exception("Line must start with a date in the form '1.'.")
                    date = int(tokens.pop(0)[:-1])
                    
                    new_holiday = CalendarDay(datetime.date(year, month, date))
                    new_holiday.type = DayType.HOLIDAY
                    new_holiday.comment = comment
                    
                    # Parse deviating work hours (optional)
                    if tokens and len(tokens) == 1:
                        new_holiday.hours = make_timedelta(tokens.pop())
                    elif tokens:
                        raise Exception("Line has too many elements.")
                    
                    self.calendar[year][month][date] = new_holiday
                elif tokens:
                    raise Exception("Unknown month for entry.")
    
    def create_user(self):
        new_user = User()
        new_user.vacation = 30
        return new_user
    
    def read_report_files(self):
        month_reports = glob.glob(os.path.join(self.settings["chronopath"], "20[0-9][0-9]-[0-1][0-9].txt"))
        
        for month_report in month_reports:
            file = os.path.split(month_report)[1]
            year = int(file[0:4])
            month = int(file[5:7])
            new_month = Month(month, year)
            new_month.add_calendar(self.calendar[year][month])

            f = open(month_report, "r")
            for line in f.readlines():
                new_day = DayReport()
                new_day.parse_string(line, month, year)
                new_month.add_report(new_day)
            
            self.months.append(new_month)
        
    def make_reports(self, filter=""):
        """
        Prints out a report in the terminal for the current month. Future
        implementation should allow more flexible output that can be configured
        in the .chrono file.
        """

        # TODO:
        # - implement filter
        
        
        
        total_flex = datetime.timedelta()
        utilised_vacation = 0
        today = datetime.date.today()
        
        for month in self.months:
            month_report = Report([10, 7, 7, 7, 7, 40])
            month_report.set_title("%s %s" % (cal.month_name[month.month],
                                              month.year))
            month_report.add_header(["Date",
                                     "Start",
                                     "End",
                                     "Hours",
                                     "Day",
                                     "Comment"])
                        
            for date, day in month.calendar.items():
                if (today.month < month.month or
                    today.month == month.month and today < day.date):
                         break
                row = []
                
                weekday = cal.weekday(month.year, month.month, date)     
                date_field = "%s %s." % (cal.day_abbr[weekday], str(date).rjust(2))
                if self.settings['color']:
                    date_field = DayType.colors[day.type] + date_field + AnsiColors.ENDC
                row.append(date_field)
                                    
                if date in month.reports:
                    report = month.reports[date]
                    day.type = report.type
                    
                    if report.start:
                        row.append(pretty_time(report.start))
                    else:
                        row += [None]
                    if report.lunch:
                        row.append(pretty_timedelta(report.lunch))
                    else:
                        row += [None]
                    if report.end:
                        row.append(pretty_time(report.end))
                        row.append(pretty_timedelta(report.hours))
                    else:
                        row += [None, None]
                    
                    # Make one comment string from multiple sources
                    comment_string = ""
                    if report.type in [DayType.S, DayType.V, DayType.VAB]:
                        deviation_type = DayType.pretty_keys[report.type]
                    else:
                        deviation_type = None
                    
                    for comment in [comment for comment in [report.comment, deviation_type, day.comment] if comment]:
                        if comment_string:
                            comment_string += ". "
                        comment_string += comment
                    row.append(comment_string)
                    if day.type == DayType.V:
                        utilised_vacation += 1
                else:
                    row += [None, None, None, None]
                    row.append(day.comment)
                
                month_report.add_row(row)
                    
            month_report.print_report()
            
            flex = month.calculate_flex()
            total_flex += flex
            print "%s+%s+%s" % ("-" * 8, "-" * 35, "-" * 35)
            print """           Flex for %s: %s""" % (cal.month_name[month.month], pretty_timedelta(flex))
            print "%s" % ("-" * 80)
        
        total_flex += self.report_archive.calculate_flex()
        utilised_vacation += self.report_archive.utilised_vacation()
        print "\nTotal flex: %s" % (pretty_timedelta(total_flex))
        print "Vacation left: %s/%s" % (self.user.vacation - utilised_vacation, self.user.vacation)
        print
    
    def new_report(self, report):
        """
        Creates a new report from a string. Should be able to handle icomplete
        strings e.g. just reporting date and start time.
        """
        # TODO:
        # - contextual stuff depending on if there allready is a started report
        #   for today etc.
        new_day = DayReport()
        new_day.parse_string(report,
                             datetime.date.today().month,
                             datetime.date.today().year)
        print new_day
        
    
    def edit_report(self, file_key):
        """
        Edits a report in external editor.
        """
        
        # TODO:
        # - Look for enviroment variables if editor is missing in .chorno
        # - Take arguments if you want to edit another file than the latest
        # - Create a new text file if new month
        
        editor_cmd = None
        if 'editor' in self.settings:
            editor_cmd = self.settings['editor']
        
        year = datetime.date.today().year 
        month = datetime.date.today().month
        if month < 10:
            month = "0%s" % month
        # Look for current month
        if file_key == None:
            file_name = os.path.join(self.settings["chronopath"], "%s-%s.txt" % (year, month))
        if editor_cmd and os.path.isfile(file_name):
            subprocess.Popen([editor_cmd, file_name],
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.STDOUT)
        else:
            raise Exception("No external editor is set")

    def setup(self):
        print "SETUP"
    
    def print_month(self):
        pass

class User(object):
    """Class representing a user i.e. an employee"""
    
    def __init__(self):
        self.name = ""
        self.id = ""
        self.employment = 0
        self.vacation = 0
        
class Archive(object):
    """
    Class representing all archived days
    """
    def __init__(self):
        self.reports = {}

    def calculate_flex(self):
        flex = datetime.timedelta()
        for date, day in self.reports.items():
            if day.hours:
                flex += (day.hours - self.standard_hours[day.reports])
        return flex
    
    def utilised_vacation(self):
        utilised_vacation = 0
        for day in self.reports.values():
            if day.type == DayType.V:
                utilised_vacation += 1
        return utilised_vacation
 
class Month(object):
    """Class representing a month"""
    def __init__(self, month, year):
        self.year = year
        self.month = month

        self.reports = {}
        self.calendar = {}
        
        for date in cal.Calendar().itermonthdates(year, month):
            if date.month == month:
                new_date = CalendarDay(date)
                if date.weekday() < 5:
                    new_date.standard_hours = datetime.timedelta(hours=8)
                    new_date.type = DayType.WEEKDAY
                else:
                    new_date.type = DayType.WEEKEND
                self.calendar[date.day] = new_date
    
    def weekends_up_to_date(self, day):
        weekends = []
        for date, weekday in cal.Calendar().itermonthdays2(self.year, self.month):
            if date > 0 and date <= day and weekday in [5, 6]:
                new_day = DayReport(date)
                new_day.type = DayType.WEEKEND
                weekends.append(new_day)
        return weekends
    
    def add_calendar(self, calendar):
        for date, day in calendar.items():
            self.calendar[date].standard_hours = day.standard_hours
            self.calendar[date].type = day.type
            self.calendar[date].comment = day.comment
    
    def add_report(self, day_report):
        self.reports[day_report.date] = day_report

    def holidays_up_to_date(self, day):
        holidays = []
        
        return holidays
    
    def calculate_flex(self):
        flex = datetime.timedelta()
        for date, day in self.reports.items():
            if day.hours:
                flex += (day.hours - self.calendar[date].standard_hours)
        return flex
    
    def all_days(self):
        # todo:
        # add weekends and holidays
        all_days = self.reports[:]
        all_days += self.holidays_up_to_date(datetime.date.today().date)
        all_days += self.weekends_up_to_date(datetime.date.today().date)
        all_days.sort(key=lambda x: x.date)
        return all_days

class Report(object):
    """Class for structuring and printing time reports"""
    def __init__(self, cols):
        self._cols = cols
        self._rows = []
        self._title = None
        self._header = []
        self._lines = True
    
    def set_title(self, title):
        self._title = title
    
    def add_header(self, header):
        assert len(header) <= len(self._cols)
        self._header = header
    
    def add_row(self, row):
        assert len(row) <= len(self._cols)
        self._rows.append(row)
        
    def print_report(self):
        if self._title:
            print self._title
        for n, h in enumerate(self._header):
            print h.ljust(self._cols[n]),
        print
        for row in self._rows:
            for n, cell in enumerate(row):
                if cell:
                    print cell.ljust(self._cols[n]),
                else:
                    print " " * self._cols[n],
            print

class AnsiColors:
    WHITE = '\033[97m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    YELLOW = '\033[93m'
    BLACK = '\033[30m'
    
    WHITE_BG = '\033[107m'
    RED_BG = '\033[101m'
    GREEN_BG = '\033[102m'
    BLUE_BG = '\033[104m'
    CYAN_BG = '\033[106m'
    MAGENTA_BG = '\033[105m'
    YELLOW_BG = '\033[103m'
    BLACK_BG = '\033[40m'
    
    BOLD = '\033[1m'
    
    ENDC = '\033[0m'

class DayType:
    NONE, WEEKDAY, WEEKEND, HOLIDAY, S, V, VAB = range(7)
    keys = ["NONE", "WEEKAY", "WEEKEND", "HOLIDAY", "S", "V", "VAB"]
    pretty_keys = ["None", "Weekday", "Weekend", "Holiday", "Sick day", "Vacation", "VAB"]
    colors = [AnsiColors.ENDC,                        # None
              AnsiColors.ENDC,                        # Weekday
              AnsiColors.BLACK + AnsiColors.CYAN_BG,  # Weekend
              AnsiColors.BLACK + AnsiColors.CYAN_BG,  # Holiday
              AnsiColors.RED,                         # Sick day
              AnsiColors.GREEN,                       # Vacation
              AnsiColors.YELLOW]                      # VAB
   

class CalendarDay(object):
    """Class representing a day in the calendar"""
    
    def __init__(self, date=None):
        self.date = date
        self.comment = None
        self.standard_hours = datetime.timedelta()
        self.type = DayType.NONE
        self.report = None

    
class DayReport(object):
    """Class representing a day in a report"""
        
    def __init__(self, date=None):
        self.date = date
        
        self.start = None
        self.end = None
        self.lunch = None
        self.deviation = None
        self.hours = None
        self.comment = None
        self.type = DayType.NONE
    
    def parse_string(self, line, month, year):
        
        # Parse comment which is only allowed last
        m = _comment_pattern.search(line)
        if m:
            if m.group(2):
                self.comment = m.group(2)
            elif m.group(5):
                self.comment = m.group(5)
            line = _comment_pattern.sub('', line)
        
        tokens = line.strip().split()
        
        # Parse date
        if tokens[0].find(".") == -1:
            raise Exception("Line must start with a date in the form '1.'.")
    
        self.date = int(tokens.pop(0)[:-1])
        
            
        # Parse special modification wich is only allowed directly after date
        if tokens[0].upper() in DayType.keys:
            self.type = getattr(DayType, tokens.pop(0).upper())
        else:
            self.type = DayType.WEEKDAY
        
        # Parse rest of tokens
        while tokens:
            token = tokens.pop(0)
            if self.start is None:
                self.start = make_datetime(token, self.date, month, year)
            elif self.lunch is None:
                self.lunch = make_timedelta(token)
            elif self.end is None:
                self.end = make_datetime(token, self.date, month, year)
                self.hours = (self.end - self.start) - self.lunch
            else:
                raise Exception("Unknown token: '%s'" % token)

_comment_pattern = re.compile("(?:(\")(.*)(\")|(\')(.*)(\'))\s*$")
_time_pattern = re.compile("^(\d{1,2})(?:\:|\.)(\d{2})$")
_timedelta_pattern = re.compile("^((?:-|\+)?\d+)(?:(?:\:|\.)(\d{2}))?$")

def make_datetime(time_string, day, month, year):
    """
    Creates a point of time.
    Valid patterns:
          1:23  -  Hours and minutes delimited by a colon.
          1.23  -  Hours and minutes delimited by a period.
         01:00  -  Optional leading zero for hours below 10.
    """
    m = _time_pattern.match(time_string)
    if m:
        hour = int(m.group(1))
        minute = int(m.group(2))
        new_time = datetime.datetime(year, month, day, hour, minute)
    else:
        new_time = None
    return new_time
    
def make_timedelta(string):
    """
    Creates a time duration. Can be both positive and negative.
    Valid patterns:
        1:23  -  Hours and minutes delimited by a colon.
        1.23  -  Hours and minutes delimited by a period.
        1     -  Just hours.
       +1:23  -  Optional plus for positive.
       -1:23  -  A minus for negative.
    """
    m = re.search('^((?:-|\+)?\d+)(?:(?:\:|\.)(\d{2}))?$', string)
    if m:
        if m.groups()[1]:
            new_delta = datetime.timedelta(hours=int(m.group(1)), minutes=int(m.group(2)))
        else:
            new_delta = datetime.timedelta(hours=int(m.group(1)))
    else:
        raise Exception("Please make this exception more specific.")
    return new_delta

def pretty_time(time):
    return time.strftime("%H:%M")
    
def pretty_timedelta(timedelta):
    if timedelta < datetime.timedelta():
        negative = True
    else:
        negative = False
    total_seconds = abs(int(timedelta.total_seconds()))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if minutes < 10:
        minutes = "0%s" % minutes
    pretty = "%s%s:%s" % ("-" * negative, hours, minutes)
    return pretty
        
    
if __name__ == '__main__':
    main()

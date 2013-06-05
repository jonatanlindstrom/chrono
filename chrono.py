#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Usage: chrono.py ( ls | setup | report | edit)
       chrono.py -h | --help

Displays amra files with or without masks.

Arguments:
  ls          List reports
  setup       Set up work info
  report      Make new report
  edit        Edit a report

Options:
  -h --help                    Print this message.
"""

from docopt import docopt
import logging
import os
import calendar as cal
import datetime
import re

def main():
    arguments = docopt(__doc__)
    chrono = Chrono()
    if arguments['ls']:
        chrono.list_reports()
    elif arguments['report']:
        chrono.new_report() 
    elif arguments['edit']:
        chrono.edit_report()
    elif arguments['setup']:
        chrono.setup()

class Chrono(object):
    
    def __init__(self):
        if not os.path.isfile("~/.chrono"):
            settings = {}
            settings["chronopath"] = "/Users/jonatan/Dropbox/AMRA/chrono/"
            self.write_dot_file(settings)
        self.settings = self.read_dot_file()
        
        # This is a hack. Later, similar info should be derived from the
        # computers clock and from files present in the chrono folder.
        self.current_month = 6
        self.current_year = 2013
        
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
            settings[key] = value
        return settings

    def list_reports(self):
        """
        Prints out a report in the terminal for the current month. Future
        implementation should allow more flexible output that can be configured
        in the .chrono file.
        """
        path = os.path.join(self.settings["chronopath"], "2013-06.txt")
        f = open(path, "r")
        month = Month(6, 2013)
        months = []
        months.append(month)
        archive = Archive()
        for line in f.readlines():
            new_day = Day()
            new_day.parse_string(line, self.current_month, self.current_year)
            month.add_day(new_day)
        print "\nReports for %s %s" % (cal.month_name[6], 2013)
        print "-----"
        print """ Day   S/V   Start   Lunch    End    Hours   Comments"""
        for day in month.all_days():
            print "%s%s%s%s%s%s%s" % ((str(day.start.day) + ".").center(6),
                                           "?".center(6),
                                           day.start.strftime("%H:%M").center(8),
                                           pretty_timedelta(day.lunch).center(8) if day.lunch else "".center(8),
                                           day.end.strftime("%H:%M").center(8) if day.end else "".center(8),
                                           pretty_timedelta(day.hours).center(8) if day.hours else "".center(8),
                                           day.comment if day.comment else "".center(8) )
        total_flex = datetime.timedelta()
        for mon in months:
            total_flex += mon.calculate_flex()
        print """-----
Flex for %s: %s
Total flex: %s
""" % (cal.month_name[6],
       pretty_timedelta(month.calculate_flex()),
       pretty_timedelta(month.calculate_flex() + archive.calculate_flex()))
    
    def new_report(self):
        """
        Creates a new report from a string. Should be able to handle icomplete
        strings e.g. just reporting date and start time.
        """
        print "NEW"
    
    def edit_report(self):
        """
        Edits a previous report.
        """
        print "EDIT"

    def setup(self):
        print "SETUP"

class Archive(object):
    """
    Class representing all archived days
    """
    def __init__(self):
        self.days = []

    def calculate_flex(self):
        flex = datetime.timedelta()
        for day in self.days:
            if day.hours:
                flex += (day.hours - self.standard_hours[day.day])
        return flex
        
class Month(object):
    """Class representing a month"""
    def __init__(self, month, year):
        self.first_day = None
        self.last_day = None
        self.days = []
        calendar = cal.Calendar()
        self.standard_hours = [0] * (cal.monthrange(year, month)[1] + 1)
        for date, weekday in calendar.itermonthdays2(year, month):
            if date:
                if weekday < 6:
                    self.standard_hours[date] = datetime.timedelta(hours=8)
        #print self.standard_hours
        #print calendar.monthdayscalendar(year, month)
        # TODO:
        # - Calculate work days for month including information from year
        #   configuration file.
    
    def add_day(self, day):
        self.days.append(day)
    
    
    def calculate_flex(self):
        flex = datetime.timedelta()
        for day in self.days:
            if day.hours:
                flex += (day.hours - self.standard_hours[day.day])
        return flex
    
    def all_days(self):
        
        return self.days
    
class Day(object):
    """Class representing a day in a report"""
    def __init__(self):
        self.day = None
        self.start = None
        self.end = None
        self.lunch = None
        self.deviation = None
        self.hours = None
        self.comment = None
        self.vacation = False
        self.sick_day = False
        self.vab = False

    
    def parse_string(self, line, month, year):
        tokens = line.strip().split()
        
        # Parse date
        if tokens[0].find(".") == -1:
            raise Exception("Line must start with a date in the form '1.'.")
    
        self.day = int(tokens[0][:-1])
        tokens.pop(0)
        
        # Parse comment which is always last or missing
        m = _comment_pattern.match(tokens[-1])
        if m:
            if m.group(2):
                self.comment = m.group(2)
            elif m.group(5):
                self.comment = m.group(5)
            tokens.pop()
        
        # Parse rest of tokens
        while tokens:
            token = tokens.pop(0)
            if self.start is None:
                self.start = make_datetime(token, self.day, month, year)
            elif self.lunch is None:
                self.lunch = make_timedelta(token)
            elif self.end is None:
                self.end = make_datetime(token, self.day, month, year)
                self.hours = (self.end - self.start) - self.lunch

        self.vacation = False
        self.sick_day = False
        self.vab = False

_comment_pattern = re.compile("(?: (\")(.*)(\")|(\')(.*)(\'))\s*$")
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
        
def pretty_timedelta(timedelta):
    hours, remainder = divmod(int(timedelta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    pretty = "%s:%s" % (hours, minutes)
    return pretty
    
if __name__ == '__main__':
    main()

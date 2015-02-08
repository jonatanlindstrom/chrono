#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Usage: chrono [options] (today | (day | month | year) [<date>])
       chrono [options] flex
       chrono [options] vacation
       chrono [options] statistics ( start | lunch | end)
       chrono [options] user
       chrono -h | --help

Options:
--set-data-folder=<folder>
-v, --verbose
"""
import os
import sys
import glob
import time
import datetime
import locale
import statistics as st
import configparser
from docopt import docopt
from chrono.parser import Parser
from chrono.day import DayType

def main():
    locale.setlocale(locale.LC_ALL, '')
    arguments = docopt(__doc__)
    if arguments['--verbose']:
        print(arguments)
    config_path = os.path.expanduser("~/.chrono2")
    config = get_config(config_path)
    reconfigured = False
    if 'Data' not in config['Paths']:
        print("Chrono requires a data folder. Specify data folder with the --set-data-folder option.")
        sys.exit(1)
    elif arguments["--set-data-folder"]:
        data_folder = os.path.abspath(os.path.expanduser(arguments["--set-data-folder"]))
        if os.path.isdir(data_folder):
            config['Paths']['Data'] = data_folder
            reconfigured = True
        else:
            raise ValueError("Couln't find folder '{}'.".format(data_folder))
    else:
        data_folder = os.path.expanduser(config['Paths']['Data'])
        parser = Parser()
        parser.parse_user_file(os.path.join(data_folder, "user.cfg"))
        year_files = [f[:4] for f in os.listdir(data_folder) if f.endswith(".cfg") and len(os.path.basename(f)) == 8]
        month_files = sorted(glob.glob(os.path.join(data_folder, "[1-2][0-9][0-9][0-9]-[0-1][0-9].txt")))

        for month_file in month_files:
            year = os.path.basename(month_file)[:4]
            if year in year_files:
                parser.parse_year_file(os.path.join(data_folder, "{}.cfg".format(year)))
                year_files.remove(year)
            parser.parse_month_file(month_file)
        if arguments['today'] or arguments['day']:
            if not arguments['<date>']:
                selected_day = parser.user.today()
            else:
                date = arguments['<date>'].split("-")
                if len(date) == 1:
                    day = int(date[0])
                    selected_day =  [d for d in parser.user.current_month().days if d.date.day == day][0]
                elif len(date) == 2:
                    month, day = date
                    month = int(month)
                    day = int(day)
                    selected_month = [m for m in parser.user.current_year().months if m.month == month][0]
                    selected_day = [d for d in selected_month.days if d.date.day == day][0]
                elif len(date) == 3:
                    year, month, day = date
                    year = int(year)
                    month = int(month)
                    day = int(day)
                    selected_year = [y for y in parser.user.years if y.year == year][0]
                    selected_month = [m for m in selected_year.months if m.month == month][0]
                    selected_day = [d for d in selected_month.days if d.date.day == day][0]
            print(selected_day)
        elif arguments['month']:
            if arguments['<date>']:
                if "-" in arguments['<date>']:
                    year, month = arguments['<date>'].split("-")
                    year = int(year)
                    month = int(month)
                else:
                    year = parser.user.current_year().year
                    month = int(arguments['<date>'])
                selected_year = [y for y in parser.user.years if y.year == year][0]
                selected_month = [m for m in selected_year.months if m.month == month][0]
            else:
                selected_month = parser.user.years[-1].months[-1]
            print()
            _print_month(selected_month)
            print("\nTotal flextime: {}".format(_pretty_timedelta(parser.user.calculate_flextime(), signed=True)))
        elif arguments['year']:
            if arguments['<date>']:
                selected_year = [year for year in parser.user.years if str(year.year) == arguments['<date>']][0]
            else:
                selected_year = parser.user.years[-1]
            for month in selected_year.months:
                _print_month(month)
                print()
        elif arguments['user']:
            print()
            print(parser.user)
            print()
        elif arguments['statistics']:
            if arguments['start']:
                mornings = [
                    datetime.timedelta(
                        hours=d.start_time.hour,
                        minutes=d.start_time.minute).total_seconds()
                    for d in parser.user.all_days()
                    if d.start_time is not None]
                print("\nStart time")
                print("-" * 17)
                print("{:<12}{}".format("Mean:", time.strftime('%H:%M', time.gmtime(st.mean(mornings)))))
                print("{:<12}{}".format("Median:", time.strftime('%H:%M', time.gmtime(st.median(mornings)))))
                print("{:<12}{}".format("Mode:", time.strftime('%H:%M', time.gmtime(st.mode(mornings)))))
                print("{:<12}{}".format("Earliest:", time.strftime('%H:%M', time.gmtime(min(mornings)))))
                print("{:<12}{}".format("Latest:", time.strftime('%H:%M', time.gmtime(max(mornings)))))
                print("-" * 17)
                print("{} values".format(len(mornings)))
                print()
            if arguments['end']:
                evenings = [
                    datetime.timedelta(
                        hours=d.end_time.hour,
                        minutes=d.end_time.minute).total_seconds()
                    for d in parser.user.all_days()
                    if d.end_time is not None]
                print("\nEnd time")
                print("-" * 17)
                print("{:<12}{}".format("Mean:", time.strftime('%H:%M', time.gmtime(st.mean(evenings)))))
                print("{:<12}{}".format("Median:", time.strftime('%H:%M', time.gmtime(st.median(evenings)))))
                print("{:<12}{}".format("Mode:", time.strftime('%H:%M', time.gmtime(st.mode(evenings)))))
                print("{:<12}{}".format("Earliest:", time.strftime('%H:%M', time.gmtime(min(evenings)))))
                print("{:<12}{}".format("Latest:", time.strftime('%H:%M', time.gmtime(max(evenings)))))
                print("-" * 17)
                print("{} values".format(len(evenings)))
                print()
        elif arguments['vacation']:
            print("Vacation left: {} / {}".format(parser.user.vacation_left(), parser.user.payed_vacation))
    if reconfigured:
        write_config(config, config_path)

def _print_month(month):
    width = 37
    print("{:^{width}}".format("{m.year}-{m.month:02} - {name}".format(m=month, name=datetime.datetime(month.year, month.month, 1).strftime("%B")), width=width))
    print("-" * width)
    for day in month.days:
        if day.day_type == DayType.working_day:
            print("{:>2}.  {}  {}  {}  {:>5}  {}  {}".format(
                day.date.day,
                day.start_time.strftime('%H:%M'), 
                _pretty_timedelta(day.lunch_duration),
                day.end_time.strftime('%H:%M'),
                _pretty_timedelta(day.deviation, signed=True) if day.deviation != datetime.timedelta() else "",
                _pretty_timedelta(day.calculate_flextime(), signed=True),
                day.comment or ""))
        elif day.day_type == DayType.vacation:
            print("{:>2}.  {:^{width}}".format(day.date.day, "V a c a t i o n", width=18))
        elif day.day_type == DayType.sick_day:
            print("{:>2}.  {:^{width}}".format(day.date.day, "S i c k   d a y", width=18))
    print("-" * width)
    print("{:>{width}}".format(_pretty_timedelta(month.calculate_flextime(), signed=True), width=width))

def _pretty_timedelta(timedelta, signed=False):
    if signed:
        template = "{:+2d}:{:02}"
    else:
        template = "{}:{:02}"
    seconds = int(timedelta.total_seconds())
    negative = seconds < 0
    hours = abs(seconds) // 3600
    minutes = abs(seconds) // 60 % 60
    if negative:
        hours = -hours
    pretty_timedelta = template.format(hours, minutes)
    return pretty_timedelta

def get_config(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    if not config.has_section('Paths'):
        config.add_section('Paths')
    return config

def write_config(config, config_path):
    with open(config_path, 'w') as config_file:
        config.write(config_file)

if __name__ == '__main__':
    main()

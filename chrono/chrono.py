#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Usage: chrono [options] flex
       chrono [options] month
       chrono [options] user
       chrono [options] vacation
       chrono [options] year [<year>]
       chrono [options] --set-data-folder=<folder>
       chrono -h | --help

Options:
-v, --verbose
"""
import os
import sys
import glob
import datetime
from docopt import docopt
from chrono.parser import Parser
from chrono.day import DayType
import configparser


def main():
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
        data_folder = config['Paths']['Data']
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

        if arguments['month']:
            print()
            month = parser.user.years[-1].months[-1]
            _print_month(month)
            print("\nTotal flextime: {}".format(_pretty_timedelta(parser.user.calculate_flextime(), signed=True)))
        elif arguments['year']:
            if arguments['<year>']:
                selected_year = [year for year in parser.user.years if str(year.year) == arguments['<year>']][0]
            else:
                selected_year = parser.user.years[-1]
            for month in selected_year.months:
                _print_month(month)
                print()
        elif arguments['user']:
            print()
            print(parser.user)
            print()
        elif arguments['flex']:
            flex = parser.user.calculate_flextime()
            print("Flextime as of {}:\n{} hours {} minutes".format(datetime.date.today(), flex.seconds//3600, (flex.seconds//60)%60))
        elif arguments['vacation']:
            print("{} / {}".format(parser.user.vacation_left(), parser.user.vacation_left() + parser.user.used_vacation()))
    if reconfigured:
        write_config(config, config_path)

def _print_month(month):
    width = 37
    print("{:^{width}}".format("{m.year}-{m.month:02}".format(m=month), width=width))
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
    pretty_timedelta = template.format(
        timedelta.days * 24 + timedelta.seconds // 3600,
        (timedelta.seconds // 60) % 60)
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

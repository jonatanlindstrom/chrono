#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Usage: chrono [options] (today | (day |  month | year) [<date>])
       chrono [options] week [<week> [<year>]]
       chrono [options] report (start | end) [<time>]
       chrono [options] report (lunch | deviation) <time>
       chrono [options] flex
       chrono [options] vacation
       chrono [options] stats (start | end) [-w | -m | -y] [--hist [--height=<height>][--bin-width=<width>]]
       chrono [options] user
       chrono [options] edit [<month>]
       chrono -h | --help

Options:
--height=<height>             Height of histogram. [default: 20]
--bin-width=<width>           Width in minutes of each bin. [default: 5]
--hist                        Print histogram
--set-data-folder=<folder>
-v, --verbose
"""
import os
import sys
from glob import glob
import time
import datetime
import locale
import statistics as st
import configparser
import subprocess

import math
from docopt import docopt

from chrono.parser import Parser
from chrono import writer
from chrono.time_utilities import pretty_timedelta
from chrono import errors


def main():
    locale.setlocale(locale.LC_ALL, '')
    arguments = docopt(__doc__)
    if arguments['--verbose']:
        print(arguments)
    config_path = os.path.expanduser("~/.chrono")
    config = get_config(config_path)
    reconfigured = False
    if 'Data' not in config['Paths']:
        print("Chrono requires a data folder. Specify data folder with the "
              "--set-data-folder option.")

        sys.exit(1)
    elif arguments["--set-data-folder"]:
        data_folder = os.path.abspath(
            os.path.expanduser(arguments["--set-data-folder"]))

        if os.path.isdir(data_folder):
            config['Paths']['Data'] = data_folder
            reconfigured = True
        else:
            raise ValueError("Couln't find folder '{}'.".format(data_folder))
    else:
        data_folder = os.path.expanduser(config['Paths']['Data'])
        parser = Parser()
        parser.parse_user_file(os.path.join(data_folder, "user.cfg"))
        year_files = [f[:4] for f in os.listdir(data_folder)
                      if f.endswith(".cfg") and len(os.path.basename(f)) == 8]

        month_files = sorted(glob(os.path.join(
            data_folder, "[1-2][0-9][0-9][0-9]-[0-1][0-9].txt")))

        for month_file in month_files:
            year = os.path.basename(month_file)[:4]
            if year in year_files:
                parser.parse_year_file(
                    os.path.join(data_folder, "{}.cfg".format(year)))

                year_files.remove(year)
            parser.parse_month_file(month_file)

        # Handling CLI commands
        if arguments['today'] or arguments['day']:
            if not arguments['<date>']:
                selected_day = parser.user.today()
            else:
                date = arguments['<date>'].split("-")
                if len(date) == 1:
                    day = int(date[0])
                    selected_day = [d for d in parser.user.current_month().days
                                    if d.date.day == day][0]

                elif len(date) == 2:
                    month, day = date
                    month = int(month)
                    day = int(day)
                    selected_month = [
                        m for m in parser.user.current_year().months
                        if m.month == month][0]

                    selected_day = [d for d in selected_month.days
                                    if d.date.day == day][0]

                elif len(date) == 3:
                    year, month, day = date
                    year = int(year)
                    month = int(month)
                    day = int(day)
                    selected_year = [y for y in parser.user.years
                                     if y.year == year][0]

                    selected_month = [m for m in selected_year.months
                                      if m.month == month][0]

                    selected_day = [d for d in selected_month.days
                                    if d.date.day == day][0]
                else:
                    raise errors.BadDateError(
                        "Date string must have between 1 and 3 elements.")

            print(selected_day)
        elif arguments['week']:
            selected_week = parser.user.current_week()
            print(selected_week)
            print("Total flextime: {}".format(pretty_timedelta(
                parser.user.calculate_flextime(), signed=True)))

        elif arguments['month']:
            if arguments['<date>']:
                if "-" in arguments['<date>']:
                    year, month = arguments['<date>'].split("-")
                    year = int(year)
                    month = int(month)
                else:
                    year = parser.user.current_year().year
                    month = int(arguments['<date>'])
                selected_year = [y for y in parser.user.years
                                 if y.year == year][0]

                selected_month = [m for m in selected_year.months
                                  if m.month == month][0]
            else:
                selected_month = parser.user.years[-1].months[-1]
            print(selected_month)
            print("Total flextime: {}".format(pretty_timedelta(
                parser.user.calculate_flextime(), signed=True)))

        elif arguments['year']:
            if arguments['<date>']:
                selected_year = [year for year in parser.user.years
                                 if str(year.year) == arguments['<date>']][0]
            else:
                selected_year = parser.user.years[-1]
            for month in selected_year.months:
                print(month)
        elif arguments['report']:
            if arguments['start']:
                start_time = (arguments['<time>'] or
                              datetime.datetime.now().strftime("%H:%M"))

                parser.user.add_day(
                    parser.user.next_workday()).report_start_time(start_time)

            elif arguments['end']:
                end_time = (arguments['<time>'] or
                            datetime.datetime.now().strftime("%H:%M"))
                parser.user.today().report_end_time(end_time)
            elif arguments['lunch']:
                parser.user.today().report_lunch_duration(arguments['<time>'])
            elif arguments["deviation"]:
                parser.user.today().report_deviation(arguments['<time>'])
            today = parser.user.today()
            month_file = os.path.join(
                data_folder, "{}.txt".format(today.date.strftime("%Y-%m")))

            writer.write_line(month_file, today.export())
        elif arguments['user']:
            print()
            print(parser.user)
            print()
        elif arguments['stats']:
            if arguments['-w']:
                selected_period = parser.user.current_week().days
            elif arguments['-m']:
                selected_period = parser.user.current_month().days
            elif arguments['-y']:
                selected_period = parser.user.current_year().days
            else:
                selected_period = parser.user.all_days()
            if arguments['start']:
                print_start_statistics(
                    selected_period,
                    histogram=arguments['--hist'],
                    bin_width=int(arguments['--bin-width']),
                    height=int(arguments['--height']))

            if arguments['end']:
                print_end_statistics(
                    selected_period,
                    histogram=arguments['--hist'],
                    bin_width=int(arguments['--bin-width']),
                    height=int(arguments['--height']))

        elif arguments['vacation']:
            print("Vacation left: {} / {}".format(
                parser.user.vacation_left(), parser.user.payed_vacation))
        elif arguments['edit']:
            if 'Editor' in config['Paths']:
                if arguments['<month>']:
                    month_string = arguments['<month>']
                else:
                    month_string = parser.user.today().date.strftime("%Y-%m")
                month_file = os.path.join(
                    data_folder, "{}.txt".format(month_string))

                if not os.path.exists(month_file):
                    raise errors.BadDateError(
                        "Couldn't find month file '{}'".format(month_file))

                command = [config['Paths']['Editor'], month_file]
                subprocess.call(command)
            else:
                print("Add an editor to your .chrono configuration file.")

    if reconfigured:
        write_config(config, config_path)


def print_end_statistics(time_period, histogram=False, bin_width=5, height=20):
    evenings = [
        datetime.timedelta(hours=day.end_time.hour, minutes=day.end_time.minute)
        for day in time_period
        if day.end_time is not None]

    header = "End Time ({} - {})".format(min(time_period).date, max(time_period).date)
    print()
    print(statistics_for_time_points(evenings, header))
    if histogram:
        print()
        print(draw_histogram(evenings, bin_width=bin_width, height=height))
    print()


def print_start_statistics(time_period, histogram=False, bin_width=5, height=20):
    mornings = [
        datetime.timedelta(hours=day.start_time.hour, minutes=day.start_time.minute)
        for day in time_period
        if day.start_time is not None]

    header = "Start Time ({} - {})".format(min(time_period).date, max(time_period).date)
    print()
    print(statistics_for_time_points(mornings, header))
    if histogram:
        print()
        print(draw_histogram(mornings, bin_width=bin_width, height=height))
    print()


def statistics_for_time_points(time_points: list, header: str) -> str:
    time_in_seconds = [t.total_seconds() for t in time_points]

    mean_time = time.strftime('%H:%M', time.gmtime(st.mean(time_in_seconds)))
    median_time = time.strftime('%H:%M', time.gmtime(st.median(time_in_seconds)))
    std_deviation = time.strftime('%H:%M', time.gmtime(st.pstdev(time_in_seconds)))
    try:
        mode_time = time.strftime('%H:%M', time.gmtime(st.mode(time_in_seconds)))
    except st.StatisticsError:
        mode_time = "-"
    min_time = time.strftime('%H:%M', time.gmtime(min(time_in_seconds)))
    max_time = time.strftime('%H:%M', time.gmtime(max(time_in_seconds)))

    value_width = 5
    key_width = len(header) - value_width

    row_format = "\n{{:<{key_width}}}{{:>{value_width}}}".format(key_width=key_width, value_width=value_width)
    delimiter = "\n" + "-" * len(header)

    stats_string = header
    stats_string += delimiter

    stats_string += row_format.format("Mean:", mean_time)
    stats_string += row_format.format("Median:", median_time)
    stats_string += row_format.format("Standard deviation:", std_deviation)
    stats_string += row_format.format("Mode:", mode_time)
    stats_string += row_format.format("Earliest:", min_time)
    stats_string += row_format.format("Latest:", max_time)
    stats_string += delimiter
    stats_string += "\n{} values".format(len(time_in_seconds))
    return stats_string


def draw_histogram(time_points: list, bin_width: int = 5, height: int = 20, staple_character: str = '▌') -> str:
    values = [t.total_seconds() // 60 for t in time_points]

    start_time = math.floor(min(time_points).seconds / 3600)
    end_time = math.ceil(max(time_points).seconds / 3600)

    number_of_bins = int((end_time * 60 - start_time * 60) / bin_width)
    bins = []
    for i in range(number_of_bins):
        low = start_time * 60 + i * bin_width
        high = start_time * 60 + i * bin_width + bin_width
        bins.append(len([t for t in values if low <= t < high]))

    histogram_string = ""
    for n in range(height, 0, -1):
        for bin_values in bins:
            character = staple_character if bin_values / max(bins) * height >= n else " "
            histogram_string += "{}".format(character)
        histogram_string += "\n"
    axis = ""
    scale = "\n"
    for n in range(start_time, end_time + 1):
        if n < end_time:
            width = int(number_of_bins / (end_time - start_time))
            axis += "+" + "-" * (width - 1)
            scale += "{:<{width}}".format(n, width=width)
        else:
            axis += "+"
            scale += str(n)
    histogram_string += axis
    histogram_string += scale
    return histogram_string


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

# -*- coding: utf-8 -*-

import datetime

import nose.tools as nt

from chrono import year
from chrono import errors
from chrono.day import DayType


class TestYear(object):
    def setup(self):
        pass

    def teardown(self):
        pass

    def test_add_empty_year(self):
        year_1 = year.Year("2014")
        nt.assert_equal(year_1.year, 2014)
        nt.assert_equal(year_1.months, [])
        nt.assert_false(year_1.complete())
        nt.assert_equal(year_1.next_workday(), "2014-01-01")
        nt.assert_equal(year_1.next_month(), "2014-01")
        nt.assert_equal(year_1.next_year(), "2015")
        nt.assert_equal(year_1.calculate_flextime(), datetime.timedelta())
        nt.assert_equal(year_1.used_vacation(), 0)
        nt.assert_equal(year_1.sick_days(), 0)

    def test_add_another_empty_year(self):
        year_1 = year.Year("2015")
        nt.assert_equal(year_1.year, 2015)
        nt.assert_equal(year_1.months, [])
        nt.assert_false(year_1.complete())
        nt.assert_equal(year_1.next_workday(), "2015-01-01")
        nt.assert_equal(year_1.next_month(), "2015-01")
        nt.assert_equal(year_1.next_year(), "2016")
        nt.assert_equal(year_1.calculate_flextime(), datetime.timedelta())
        nt.assert_equal(year_1.used_vacation(), 0)
        nt.assert_equal(year_1.sick_days(), 0)

    def test_report_day_to_year(self):
        year_1 = year.Year("2013")
        day_1 = year_1.add_day("2013-01-01")
        nt.assert_equal(day_1.date,
                        datetime.datetime(year=2013, month=1, day=1).date())

        nt.assert_equal(len(year_1.months), 1)
        nt.assert_equal(year_1.months[0].year, 2013)
        nt.assert_equal(year_1.months[0].month, 1)
        nt.assert_equal(len(year_1.months[0].days), 1)
        nt.assert_equal(year_1.months[0].days[0], day_1)

        nt.assert_equal(year_1.next_workday(), "2013-01-02")
        nt.assert_equal(year_1.next_month(), "2013-02")

    def test_report_full_month(self):
        year_1 = year.Year("2014")
        while year_1.next_workday()[:7] == "2014-01":
            day_1 = year_1.add_day(year_1.next_workday())
            day_1.report("8:00", "1:00", "17:00")
        nt.assert_true(year_1.months[0].complete())
    
    def test_report_full_year(self):
        year_1 = year.Year("2014")
        while year_1.next_workday() != "2015-01-01":
            day_1 = year_1.add_day(year_1.next_workday())
            day_1.report("8:00", "1:00", "17:00")
        nt.assert_equal(len(year_1.months), 12)
        nt.assert_true(year_1.complete())

    def test_calculate_flextime(self):
        year_1 = year.Year("2013")
        nt.assert_equal(year_1.calculate_flextime(), datetime.timedelta())
        year_1.add_day("2013-01-01").report("8:00", "0:30", "17:00")
        nt.assert_equal(year_1.calculate_flextime(),
                        datetime.timedelta(minutes=30))

    def test_sick_days(self):
        year_1 = year.Year("2013")
        nt.assert_equal(year_1.sick_days(), 0)
        year_1.add_day("2013-01-01").day_type = DayType.sick_day
        nt.assert_equal(year_1.sick_days(), 1)

    def test_used_vacation(self):
        year_1 = year.Year("2013")
        nt.assert_equal(year_1.used_vacation(), 0)
        year_1.add_day("2013-01-01").day_type = DayType.vacation
        nt.assert_equal(year_1.used_vacation(), 1)

    def test_add_day_wrong(self):
        year_1 = year.Year("2014")
        nt.assert_raises_regexp(
            errors.ReportError,
            "^New date string didn't match year. 2014 doesn't include "
            "2015-01-01.$",
            year_1.add_day,
            "2015-01-01")

        year_1 = year.Year("2015")
        nt.assert_raises_regexp(
            errors.ReportError,
            "^New date string didn't match year. 2015 doesn't include "
            "2014-01-01.$",
            year_1.add_day,
            "2014-01-01")

    def test_calculate_flextime_with_incomming_flex(self):
        year_1 = year.Year("2014",
                           flextime=datetime.timedelta(hours=3, minutes=14))

        nt.assert_equal(year_1.calculate_flextime(),
                        datetime.timedelta(hours=3, minutes=14))

        year_1.add_day("2014-01-01").report("10:00", "1:29", "16:00")
        nt.assert_equal(year_1.calculate_flextime(),
                        datetime.timedelta(minutes=-15))

    def test_add_year_with_forced_start_date(self):
        year_1 = year.Year("2014", start_date="2014-12-01")
        nt.assert_equal(year_1.next_workday(), "2014-12-01")
        nt.assert_false(year_1.complete())
        while year_1.next_workday() != "2015-01-01":
            day_1 = year_1.add_day(year_1.next_workday())
            day_1.report("8:00", "1:00", "17:00")
        nt.assert_true(year_1.complete())
        nt.assert_equal(len(year_1.months), 1)

    def test_add_another_year_with_forced_start_date(self):
        year_1 = year.Year("2013", start_date="2013-09-01")
        nt.assert_equal(year_1.next_workday(), "2013-09-02")
        nt.assert_false(year_1.complete())
        while year_1.next_workday() != "2014-01-01":
            day_1 = year_1.add_day(year_1.next_workday())
            day_1.report("8:00", "1:00", "17:00")
        nt.assert_true(year_1.complete())
        nt.assert_equal(len(year_1.months), 4)

    def test_add_year_with_holidays(self):
        year_1 = year.Year("2014")
        nt.assert_equal(year_1.next_workday(), "2014-01-01")
        year_1.add_holiday("2014-01-01", "New years day")
        nt.assert_equal(year_1.next_workday(), "2014-01-02")
        year_1.add_day("2014-01-02").report("8:00", "1:00", "17:00")
        nt.assert_equal(year_1.calculate_flextime(), datetime.timedelta())
        year_1.add_holiday("2014-01-02", "Ancestry day")
        nt.assert_equal(year_1.calculate_flextime(),
                        datetime.timedelta(hours=8))

    def test_add_year_with_bad_arguments(self):
        nt.assert_raises_regexp(
            errors.BadDateError,
            "Argument year_string must be a string, was \"int\"\.",
            year.Year,
            2014)

        nt.assert_raises_regexp(
            errors.BadDateError,
            "Argument year_string must be a string, was \"datetime\"\.",
            year.Year,
            datetime.datetime(year=2014, month=1, day=1))

        nt.assert_raises_regexp(
            errors.BadDateError,
            "Argument year_string must be a year \(e\.g\. \"YYYY\"\), was "
            "\"Twenty fourteen\"\.",
            year.Year,
            "Twenty fourteen")

        nt.assert_raises_regexp(
            errors.BadDateError,
            "Argument year_string must be a year \(e\.g\. \"YYYY\"\), was "
            "\"14\"\.",
            year.Year,
            "14")

        nt.assert_raises_regexp(
            errors.BadDateError,
            "Argument flextime must be a timedelta object, was \"int\"\.",
            year.Year,
            "2014",
            flextime=5)

        nt.assert_raises_regexp(
            errors.BadDateError,
            "Argument flextime must be a timedelta object, was \"str\"\.",
            year.Year,
            "2014",
            flextime="5 hours")

        nt.assert_raises_regexp(
            errors.BadDateError,
            "Argument start_date must be a string, was \"datetime\"\.",
            year.Year,
            "2014",
            start_date=datetime.datetime(year=2014, month=4, day=1))

        nt.assert_raises_regexp(
            errors.BadDateError,
            "Argument start_date must be a string, was \"int\"\.",
            year.Year,
            "2014",
            start_date=2)

        nt.assert_raises_regexp(
            errors.BadDateError,
            "Argument start_date must be a ISO date string \(e\.g\. "
            "\"YYYY-MM-DD\", was \"1/4 2014\".",
            year.Year,
            "2014",
            start_date="1/4 2014")

        nt.assert_raises_regexp(
            errors.BadDateError,
            "Argument start_date must be a ISO date string \(e\.g\. "
            "\"YYYY-MM-DD\", was \"4/1/2014\".",
            year.Year,
            "2014",
            start_date="4/1/2014")
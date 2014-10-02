# -*- coding: utf-8 -*-

import nose.tools as nt
import datetime
from chrono import month
from chrono import errors
from chrono.day import DayType


class TestMonth(object):
    def setup(self):
        pass

    def teardown(self):
        pass

    def test_bad_month(self):
        nt.assert_raises_regex(errors.BadDateError,
                               "^Bad date string: \"2014-09-01\"$",
                               month.Month,
                               "2014-09-01")

    def test_add_day(self):
        month_1 = month.Month("2014-09")
        nt.assert_equal(len(month_1.days), 0)
        day_1 = month_1.add_day("2014-09-01")
        nt.assert_equal(len(month_1.days), 1)
        nt.assert_raises_regex(
            errors.ReportError,
            "^New days can't be added while the report for a previous day is "
            "incomplete.$",
            month_1.add_day,
            "2014-09-02")
        day_1.report_start_time("8:45")
        day_1.report_lunch_duration("0:30")
        day_1.report_end_time("17:30")

        day_2 = month_1.add_day("2014-09-02")
        day_2.report_start_time("8:20")
        day_2.report_lunch_duration("0:45")
        day_2.report_end_time("17:10")
        nt.assert_raises_regex(
            errors.ReportError,
            "^New work days must be added consecutively. Expected 2014-09-03, "
            "got 2014-09-04.$",
            month_1.add_day,
            "2014-09-04")

    def test_next_workday(self):
        month_1 = month.Month("2014-09")
        nt.assert_equal(month_1.next_workday(), "2014-09-01")
        month_1.add_day("2014-09-01").report("10:00", "0:50", "17:15")
        nt.assert_equal(month_1.next_workday(), "2014-09-02")
        month_1.add_day("2014-09-02").report("08:00", "1:00", "15:45")
        month_1.add_day("2014-09-03").report("09:00", "1:20", "17:45")
        month_1.add_day("2014-09-04").report("08:50", "0:30", "18:00")
        month_1.add_day("2014-09-05").report("08:25", "1:00", "17:30")
        month_1.add_day("2014-09-08").report("09:10", "0:45", "16:50")
        nt.assert_equal(month_1.next_workday(), "2014-09-09")

    def test_next_workday_end_of_year(self):
        month_1 = month.Month("2013-12")
        month_1.add_day("2013-12-02").report("08:00", "1:00", "17:00")
        month_1.add_day("2013-12-03").report("08:00", "1:00", "17:00")
        month_1.add_day("2013-12-04").report("08:00", "1:00", "17:00")
        month_1.add_day("2013-12-05").report("08:00", "1:00", "17:00")
        month_1.add_day("2013-12-06").report("08:00", "1:00", "17:00")
        month_1.add_day("2013-12-09").report("08:00", "1:00", "17:00")
        month_1.add_day("2013-12-10").report("08:00", "1:00", "17:00")
        month_1.add_day("2013-12-11").report("08:00", "1:00", "17:00")
        month_1.add_day("2013-12-12").report("08:00", "1:00", "17:00")
        month_1.add_day("2013-12-13").report("08:00", "1:00", "17:00")
        month_1.add_day("2013-12-16").report("08:00", "1:00", "17:00")
        month_1.add_day("2013-12-17").report("08:00", "1:00", "17:00")
        month_1.add_day("2013-12-18").report("08:00", "1:00", "17:00")
        month_1.add_day("2013-12-19").report("08:00", "1:00", "17:00")
        month_1.add_day("2013-12-20").report("08:00", "1:00", "17:00")
        month_1.add_day("2013-12-23").report("08:00", "1:00", "17:00")
        month_1.add_day("2013-12-24").report("08:00", "1:00", "17:00")
        month_1.add_day("2013-12-25").report("08:00", "1:00", "17:00")
        month_1.add_day("2013-12-26").report("08:00", "1:00", "17:00")
        month_1.add_day("2013-12-27").report("08:00", "1:00", "17:00")
        month_1.add_day("2013-12-30").report("08:00", "1:00", "17:00")
        month_1.add_day("2013-12-31").report("08:00", "1:00", "17:00")
        nt.assert_equal(month_1.next_workday(), "2014-01-01")

    def test_add_day_wrong_month(self):
        month_1 = month.Month("2014-09")
        nt.assert_raises_regex(
            errors.ReportError,
            "^New date string didn't match month. 2014-09 doesn't include "
            "2014-10-01.$",
            month_1.add_day,
            "2014-10-01")

    def test_flextime(self):
        month_1 = month.Month("2014-09")
        nt.assert_equal(month_1.calculate_flextime(), datetime.timedelta())
        day_1 = month_1.add_day("2014-09-01")
        day_1.report_start_time("8:00")
        day_1.report_lunch_duration("0:30")
        day_1.report_end_time("17:00")
        nt.assert_equal(month_1.calculate_flextime(),
                        datetime.timedelta(minutes=30))

        day_2 = month_1.add_day("2014-09-02")
        day_2.report_start_time("9:00")
        day_2.report_lunch_duration("1:00")
        day_2.report_end_time("17:00")
        nt.assert_equal(month_1.calculate_flextime(),
                        datetime.timedelta(minutes=-30))

        day_3 = month_1.add_day("2014-09-03")
        day_3.report_start_time("8:00")
        day_3.report_lunch_duration("0:45")
        day_3.report_end_time("18:00")
        nt.assert_equal(month_1.calculate_flextime(),
                        datetime.timedelta(minutes=45))

    def test_complete(self):
        month_1 = month.Month("2014-09")
        nt.assert_false(month_1.complete())

    def test_register_holidays(self):
        month_1 = month.Month("2014-09")
        month_1.add_day("2014-09-01").report("08:00", "1:00", "17:00")
        month_1.add_holiday("2014-09-01", "Random Acts of Kindness Day")
        nt.assert_equal(month_1.calculate_flextime(),
                        datetime.timedelta(hours=8))

        month_1.add_holiday("2014-09-02", "Unbirthday")
        nt.assert_equal(month_1.next_workday(), "2014-09-03")

    def test_calulate_sickdays(self):
        month_1 = month.Month("2014-09")
        nt.assert_equal(month_1.sick_days(), 0)
        day_1 = month_1.add_day("2014-09-01")
        day_1.day_type = DayType.sick_day
        nt.assert_equal(month_1.sick_days(), 1)

    def test_alculate_used_vacation(self):
        month_1 = month.Month("2014-09")
        day_1 = month_1.add_day("2014-09-01")
        nt.assert_equal(month_1.used_vacation(), 0)
        day_1.day_type = DayType.vacation
        nt.assert_equal(month_1.used_vacation(), 1)

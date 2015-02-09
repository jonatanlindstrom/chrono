# -*- coding: utf-8 -*-

import datetime

import nose.tools as nt

from chrono import month
from chrono import errors
from chrono.day import DayType


class TestMonth(object):
    def setup(self):
        pass

    def teardown(self):
        pass

    def test_bad_month(self):
        nt.assert_raises_regexp(errors.BadDateError,
                                "^Bad date string: \"2014-09-01\"$",
                                month.Month,
                                "2014-09-01")

    def test_empty_month(self):
        month_1 = month.Month("2014-09")
        nt.assert_equal(month_1.year, 2014)
        nt.assert_equal(month_1.month, 9)
        nt.assert_equal(month_1.next_workday(), "2014-09-01")
        nt.assert_equal(month_1.next_month(), "2014-10")

    def test_add_day(self):
        month_1 = month.Month("2014-09")
        nt.assert_equal(len(month_1.days), 0)
        day_1 = month_1.add_day("2014-09-01")
        nt.assert_equal(len(month_1.days), 1)
        nt.assert_raises_regexp(
            errors.ReportError,
            "^New days can't be added while the report for a previous day is "
            "incomplete.$",
            month_1.add_day,
            "2014-09-02")
        day_1.report("8:45", "0:30", "17:30")

        day_2 = month_1.add_day("2014-09-02")
        day_2.report("8:20", "0:45", "17:10")
        nt.assert_raises_regexp(
            errors.ReportError,
            "^New work days must be added consecutively. Expected 2014-09-03, "
            "got 2014-09-04.$",
            month_1.add_day,
            "2014-09-04")

        nt.assert_raises_regexp(
            errors.ReportError,
            "^Date 2014-09-02 already added to month.$",
            month_1.add_day,
            "2014-09-02")

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

    def test_next_month(self):
        month_1 = month.Month("2014-09")
        nt.assert_equal(month_1.next_month(), "2014-10")
        month_1 = month.Month("2014-10")
        nt.assert_equal(month_1.next_month(), "2014-11")
        month_1 = month.Month("2014-11")
        nt.assert_equal(month_1.next_month(), "2014-12")
        month_1 = month.Month("2014-12")
        nt.assert_equal(month_1.next_month(), "2015-01")

    def test_flextime(self):
        month_1 = month.Month("2014-09")
        nt.assert_equal(month_1.calculate_flextime(), datetime.timedelta())
        day_1 = month_1.add_day("2014-09-01")
        day_1.report("8:00", "0:30", "17:00")
        nt.assert_equal(month_1.calculate_flextime(),
                        datetime.timedelta(minutes=30))

        day_2 = month_1.add_day("2014-09-02")
        day_2.report("9:00", "1:00", "17:00")
        nt.assert_equal(month_1.calculate_flextime(),
                        datetime.timedelta(minutes=-30))

        day_3 = month_1.add_day("2014-09-03")
        day_3.report("8:00", "0:45", "18:00")
        nt.assert_equal(month_1.calculate_flextime(),
                        datetime.timedelta(minutes=45))

    def test_complete(self):
        month_1 = month.Month("2014-09")
        nt.assert_false(month_1.complete())
        while month_1.next_workday().startswith("2014-09-"):
            day_1 = month_1.add_day(month_1.next_workday())
            day_1.report("8:00", "1:00", "17:00")
        nt.assert_true(month_1.complete())

        month_2 = month.Month("2014-12")
        nt.assert_false(month_2.complete())
        while month_2.next_workday().startswith("2014-12-"):
            day_2 = month_2.add_day(month_2.next_workday())
            day_2.report("8:00", "1:00", "17:00")
        nt.assert_true(month_2.complete())
        
    def test_register_holidays(self):
        month_1 = month.Month("2014-09")
        day_1 = month_1.add_day("2014-09-01")
        day_1.report("08:00", "1:00", "17:00")
        month_1.add_holiday("2014-09-01", "Random Acts of Kindness Day")
        nt.assert_equal(day_1.get_info(), "Random Acts of Kindness Day")
        nt.assert_equal(month_1.calculate_flextime(),
                        datetime.timedelta(hours=8))

        month_1.add_holiday("2014-09-02", "Unbirthday")
        nt.assert_equal(month_1.next_workday(), "2014-09-03")
        day_2 = month_1.add_day("2014-09-02")
        nt.assert_equal(day_2.get_info(), "Unbirthday")

    def test_calulate_sickdays(self):
        month_1 = month.Month("2014-09")
        nt.assert_equal(month_1.sick_days(), 0)
        day_1 = month_1.add_day("2014-09-01")
        day_1.set_type(DayType.sick_day)
        nt.assert_equal(month_1.sick_days(), 1)

    def test_calculate_used_vacation(self):
        month_1 = month.Month("2014-09")
        day_1 = month_1.add_day("2014-09-01")
        nt.assert_equal(month_1.used_vacation(), 0)
        day_1.set_type(DayType.vacation)
        nt.assert_equal(month_1.used_vacation(), 1)

    def test_calculate_used_vacation_for_date(self):
        month_1 = month.Month("2014-09")
        month_1.add_day("2014-09-01").set_type(DayType.vacation)
        month_1.add_day("2014-09-02").set_type(DayType.vacation)
        nt.assert_equal(month_1.used_vacation(date_string="2014-08-31"), 0)
        nt.assert_equal(month_1.used_vacation(date_string="2014-09-01"), 1)
        nt.assert_equal(month_1.used_vacation(date_string="2014-09-02"), 2)

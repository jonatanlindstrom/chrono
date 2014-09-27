# -*- coding: utf-8 -*-

import nose.tools as nt
import datetime
from chrono import month
from chrono import errors

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
            "^New work days must be added consecutively.$",
            month_1.add_day,
            "2014-09-04")

    def test_next_workday(self):
        month_1 = month.Month("2014-09")
        nt.assert_equal(month_1.next_workday(), "2014-09-01")
        day = month_1.add_day("2014-09-01")
        day.report("10:00", "0:50", "17:15")
        nt.assert_equal(month_1.next_workday(), "2014-09-02")
        month_1.add_day("2014-09-02").report("08:00", "1:00", "15:45")
        month_1.add_day("2014-09-03").report("09:00", "1:20", "17:45")
        month_1.add_day("2014-09-04").report("08:50", "0:30", "18:00")
        month_1.add_day("2014-09-05").report("08:25", "1:00", "17:30")
        month_1.add_day("2014-09-08").report("09:10", "0:45", "16:50")
    
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
        

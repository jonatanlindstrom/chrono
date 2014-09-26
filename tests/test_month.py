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
        month_1.add_day("2014-09-01")
        nt.assert_equal(len(month_1.days), 1)
        nt.assert_raises_regex(
            errors.ReportError,
            "^A new day can't be added until all previous days are complete.$",
            month_1.add_day,
            "2014-09-02")
    
    def test_add_day_wrong_month(self):
        pass

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

# -*- coding: utf-8 -*-

import nose.tools as nt
import datetime
import month
import errors

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

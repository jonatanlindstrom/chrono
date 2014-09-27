# -*- coding: utf-8 -*-

import nose.tools as nt
import datetime
from chrono import archive
from chrono import month
from chrono import errors

class TestArchive(object):
    def setup(self):
        pass

    def test_archive_month(self):
        month_archive = archive.Archive()
        month_1 = month.Month("2014-09")
        nt.assert_raises_regex(errors.ReportError,
                               "^Month still has unreported workdays and "
                               "can't be archived.$",
                               month_archive.archive_month,
                               month_1)

        next_day = month_1.next_workday()
        while next_day.startswith("2014-09-"):
            month_1.add_day(next_day).report("8:00", "1:00", "17:00")
            next_day = month_1.next_workday()
        month_archive.archive_month(month_1)
        nt.assert_true(month_1 in month_archive.months)

    def test_calculate_flextime_one_month(self):
        month_archive = archive.Archive()
        nt.assert_equal(month_archive.calculate_flextime(),
                        datetime.timedelta())

        month_1 = month.Month("2014-09")
        next_day = month_1.next_workday()
        while next_day.startswith("2014-09-"):
            month_1.add_day(next_day).report("8:00", "1:00", "17:01")
            next_day = month_1.next_workday()
        expected_flex = len(month_1.days) * datetime.timedelta(minutes=1)
        month_archive.archive_month(month_1)
        nt.assert_equal(month_archive.calculate_flextime(), expected_flex) 

    def test_calculate_flextime_multiple_months(self):
        month_archive = archive.Archive()
        month_1 = month.Month("2014-09")
        next_day = month_1.next_workday()
        while next_day.startswith("2014-09-"):
            month_1.add_day(next_day).report("8:00", "1:00", "17:05")
            next_day = month_1.next_workday()

        month_2 = month.Month("2014-10")
        next_day = month_2.next_workday()
        while next_day.startswith("2014-10-"):
            month_2.add_day(next_day).report("8:00", "1:00", "16:50")
            next_day = month_2.next_workday()

        month_3 = month.Month("2014-11")
        next_day = month_3.next_workday()
        while next_day.startswith("2014-11-"):
            month_3.add_day(next_day).report("8:00", "1:00", "17:01")
            next_day = month_3.next_workday()

        month_archive.archive_month(month_1)
        expected_flex = len(month_1.days) * datetime.timedelta(minutes=5)
        nt.assert_equal(month_archive.calculate_flextime(), expected_flex)

        month_archive.archive_month(month_2)
        expected_flex += len(month_2.days) * datetime.timedelta(minutes=-10)
        nt.assert_equal(month_archive.calculate_flextime(), expected_flex)

        month_archive.archive_month(month_3)
        expected_flex += len(month_3.days) * datetime.timedelta(minutes=1)
        nt.assert_equal(month_archive.calculate_flextime(), expected_flex)

# -*- coding: utf-8 -*-

import nose.tools as nt
import datetime
from chrono import archive
from chrono import month
from chrono import errors
from chrono.day import DayType


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
            month_2.add_day(next_day).report("8:10", "1:00", "17:00")
            next_day = month_2.next_workday()

        month_3 = month.Month("2014-11")
        next_day = month_3.next_workday()
        while next_day.startswith("2014-11-"):
            month_3.add_day(next_day).report("8:00", "0:30", "17:00")
            next_day = month_3.next_workday()

        month_archive.archive_month(month_1)
        expected_flex = len(month_1.days) * datetime.timedelta(minutes=5)
        nt.assert_equal(month_archive.calculate_flextime(), expected_flex)

        month_archive.archive_month(month_2)
        expected_flex += len(month_2.days) * datetime.timedelta(minutes=-10)
        nt.assert_equal(month_archive.calculate_flextime(), expected_flex)

        month_archive.archive_month(month_3)
        expected_flex += len(month_3.days) * datetime.timedelta(minutes=30)
        nt.assert_equal(month_archive.calculate_flextime(), expected_flex)

    def test_used_vacation(self):
        month_archive = archive.Archive()
        month_1 = month.Month("2014-09")
        day_1 = month_1.add_day(month_1.next_workday())
        day_1.day_type = DayType.vacation
        next_day = month_1.next_workday()
        while next_day.startswith("2014-09-"):
            month_1.add_day(next_day).report("8:00", "1:00", "17:05")
            next_day = month_1.next_workday()
        month_archive.archive_month(month_1)

        month_2 = month.Month("2014-10")
        day_2 = month_2.add_day(month_2.next_workday())
        day_2.day_type = DayType.vacation
        day_3 = month_2.add_day(month_2.next_workday())
        day_3.day_type = DayType.vacation
        next_day = month_2.next_workday()
        while next_day.startswith("2014-10-"):
            month_2.add_day(next_day).report("8:10", "1:00", "17:00")
            next_day = month_2.next_workday()
        month_archive.archive_month(month_2)

        nt.assert_equal(month_archive.used_vacation(), 3)

    def test_next_month(self):
        month_archive = archive.Archive()
        nt.assert_equal(month_archive.next_month(), "")
        month_1 = month.Month("2013-11")
        next_day = month_1.next_workday()
        while next_day.startswith("2013-11-"):
            month_1.add_day(next_day).report("8:00", "1:00", "17:00")
            next_day = month_1.next_workday()
        month_archive.archive_month(month_1)
        nt.assert_true(month_archive.next_month(), "2013-12")

        month_2 = month.Month("2013-12")
        next_day = month_2.next_workday()
        while next_day.startswith("2013-12-"):
            month_2.add_day(next_day).report("8:00", "1:00", "17:00")
            next_day = month_2.next_workday()
        month_archive.archive_month(month_2)
        nt.assert_true(month_archive.next_month(), "2014-01")

    def test_archive_same_month_twice(self):
        month_archive = archive.Archive()
        month_1 = month.Month("2014-09")
        next_day = month_1.next_workday()
        while next_day.startswith("2014-09-"):
            month_1.add_day(next_day).report("8:00", "1:00", "17:00")
            next_day = month_1.next_workday()
        month_archive.archive_month(month_1)
        nt.assert_raises_regex(errors.ReportError,
                               "^Month {}-{} is allready archived.$".format(
                                   month_1.year, month_1.month),
                               month_archive.archive_month,
                               month_1)

    def test_archive_nonsequential(self):
        month_archive = archive.Archive()
        month_1 = month.Month("2014-09")
        next_day = month_1.next_workday()
        while next_day.startswith("2014-09-"):
            month_1.add_day(next_day).report("8:00", "1:00", "17:00")
            next_day = month_1.next_workday()

        month_2 = month.Month("2014-11")
        next_day = month_2.next_workday()
        while next_day.startswith("2014-11-"):
            month_2.add_day(next_day).report("8:00", "1:00", "17:00")
            next_day = month_2.next_workday()

        month_archive.archive_month(month_1)
        nt.assert_raises_regex(errors.ReportError,
                               "^Months must be archived sequentially. "
                               "Expected 2014-10, got 2014-11.$",
                               month_archive.archive_month,
                               month_2)


# -*- coding: utf-8 -*-

from datetime import date
from datetime import timedelta

import nose.tools as nt

from chrono import week
from chrono import day
from chrono import errors


class TestWeek(object):
    def setup(self):
        pass

    def teardown(self):
        pass

    def test_create_week_with_year_and_number(self):
        week_7 = week.Week(2015, 7)
        nt.assert_equal(week_7.number, 7)
        nt.assert_equal(week_7.year, 2015)
        nt.assert_true(isinstance(week_7.monday, day.Day))
        nt.assert_equal(week_7.monday.date, date(2015, 2, 9))
        nt.assert_equal(week_7.tuesday.date, date(2015, 2, 10))
        nt.assert_equal(week_7.wednesday.date, date(2015, 2, 11))
        nt.assert_equal(week_7.thursday.date, date(2015, 2, 12))
        nt.assert_equal(week_7.friday.date, date(2015, 2, 13))
        nt.assert_equal(week_7.saturday.date, date(2015, 2, 14))
        nt.assert_equal(week_7.sunday.date, date(2015, 2, 15))

    def test_create_week_from_one_day(self):
        day_1 = day.Day("2015-02-16")
        week_8 = week.Week.from_days(day_1)
        nt.assert_equal(week_8.number, 8)
        nt.assert_equal(week_8.year, 2015)
        nt.assert_is(week_8.monday, day_1)
        nt.assert_equal(week_8.tuesday.date, date(2015, 2, 17))
        nt.assert_equal(week_8.wednesday.date, date(2015, 2, 18))
        nt.assert_equal(week_8.thursday.date, date(2015, 2, 19))
        nt.assert_equal(week_8.friday.date, date(2015, 2, 20))
        nt.assert_equal(week_8.saturday.date, date(2015, 2, 21))
        nt.assert_equal(week_8.sunday.date, date(2015, 2, 22))

    def test_create_week_from_two_days(self):
        day_1 = day.Day("2015-02-23")
        day_2 = day.Day("2015-02-24")
        week_9 = week.Week.from_days(day_1, day_2)
        nt.assert_equal(week_9.number, 9)
        nt.assert_equal(week_9.year, 2015)
        nt.assert_is(week_9.monday, day_1)
        nt.assert_is(week_9.tuesday, day_2)
        nt.assert_equal(week_9.wednesday.date, date(2015, 2, 25))
        nt.assert_equal(week_9.thursday.date, date(2015, 2, 26))
        nt.assert_equal(week_9.friday.date, date(2015, 2, 27))
        nt.assert_equal(week_9.saturday.date, date(2015, 2, 28))
        nt.assert_equal(week_9.sunday.date, date(2015, 3, 1))

    def test_create_week_from_seven_days(self):
        day_1 = day.Day("2015-03-02")
        day_2 = day.Day("2015-03-03")
        day_3 = day.Day("2015-03-04")
        day_4 = day.Day("2015-03-05")
        day_5 = day.Day("2015-03-06")
        day_6 = day.Day("2015-03-07")
        day_7 = day.Day("2015-03-08")

        week_10 = week.Week.from_days(
            day_1, day_2, day_3, day_4, day_5, day_6, day_7)

        nt.assert_equal(week_10.number, 10)
        nt.assert_equal(week_10.year, 2015)
        nt.assert_is(week_10.monday, day_1)
        nt.assert_is(week_10.tuesday, day_2)
        nt.assert_is(week_10.wednesday, day_3)
        nt.assert_is(week_10.thursday, day_4)
        nt.assert_is(week_10.friday, day_5)
        nt.assert_is(week_10.saturday, day_6)
        nt.assert_is(week_10.sunday, day_7)

    def test_create_week_with_duplicate_days_should_raise(self):
        any_day = day.Day("2015-03-15")

        nt.assert_raises_regexp(
            errors.BadDateError,
            "The same date \(2015-03-15\) was added multiple times to week\.",
            week.Week.from_days,
            any_day,
            any_day)

        another_day = day.Day("2015-03-16")
        same_day = day.Day("2015-03-16")

        nt.assert_raises_regexp(
            errors.BadDateError,
            "The same date \(2015-03-16\) was added multiple times to week\.",
            week.Week.from_days,
            another_day,
            same_day)

    def test_create_week_with_days_from_different_weeks_should_raise(self):
        day_1 = day.Day("2015-01-01")
        day_2 = day.Day("2015-07-01")

        nt.assert_raises_regexp(
            errors.BadDateError,
            "All added days doesn't belong to the same week\.",
            week.Week.from_days,
            day_1,
            day_2)

    def test_get_flextime_for_week_with_one_workday(self):
        day_1 = day.Day("2015-02-16")
        day_1.report("8:00", "1:00", "17:15")
        week_1 = week.Week.from_days(day_1)
        nt.assert_equal(week_1.calculate_flextime(), timedelta(minutes=15))

    def test_get_flextime_for_week_with_five_workdays(self):
        day_1 = day.Day("2015-02-16")
        day_1.report("8:00", "1:00", "17:01")

        day_2 = day.Day("2015-02-17")
        day_2.report("8:00", "1:00", "16:54")

        day_3 = day.Day("2015-02-18")
        day_3.report("8:00", "1:00", "18:00")

        day_4 = day.Day("2015-02-19")
        day_4.report("8:00", "1:00", "16:00")

        day_5 = day.Day("2015-02-20")
        day_5.report("8:00", "1:00", "16:55")

        week_1 = week.Week.from_days(day_1, day_2, day_3, day_4, day_5)
        nt.assert_equal(week_1.calculate_flextime(), timedelta(minutes=-10))

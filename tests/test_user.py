# -*- coding: utf-8 -*-

import nose.tools as nt
import datetime
from chrono import user
from chrono import day
from chrono import year
from chrono import errors


class TestParseUserFile(object):
    def setup(self):
        pass

    def teardown(self):
        pass

    def test_create_new_user_default(self):
        user_1 = user.User()
        nt.assert_equal(user_1.name, "")
        nt.assert_equal(user_1.payed_vacation, 0)
        nt.assert_equal(user_1.vacation_month, 1)
        nt.assert_equal(user_1.employment, 100)
        nt.assert_equal(user_1.employed_date, None)

    def test_create_new_user_specific_data(self):
        user_1 = user.User(name="Mrs. Teapot",
                           employed_date="2014-05-01",
                           employment=75,
                           payed_vacation=30,
                           vacation_month=4)
        nt.assert_equal(user_1.name, "Mrs. Teapot")
        nt.assert_equal(user_1.payed_vacation, 30)
        nt.assert_equal(user_1.vacation_month, 4)
        nt.assert_equal(user_1.employment, 75)
        nt.assert_equal(user_1.employed_date,
                        datetime.datetime(year=2014, month=5, day=1).date())

    def test_next_workday(self):
        user_1 = user.User(employed_date="2014-09-01")
        nt.assert_equal(user_1.next_workday(), "2014-09-01")
        user_2 = user.User(employed_date="2014-11-01")
        nt.assert_equal(user_2.next_workday(), "2014-11-03")

    def test_next_month(self):
        user_1 = user.User(employed_date="2014-09-01")
        nt.assert_equal(user_1.next_month(), "2014-09")
        user_1.add_day(user_1.next_workday()).report("8:00", "1:00", "17:00")
        nt.assert_equal(user_1.next_month(), "2014-10")
        while user_1.next_workday() != "2014-10-01":
            user_1.add_day(user_1.next_workday()).report(
                "8:00", "1:00", "17:00")
        nt.assert_equal(user_1.next_month(), "2014-10")

    def test_next_year(self):
        user_1 = user.User(employed_date="2014-12-01")
        nt.assert_equal(user_1.next_year(), "2015")
        while user_1.next_workday() != "2015-01-01":
            user_1.add_day(user_1.next_workday()).report(
                "8:00", "1:00", "17:00")
        user_1.add_day(user_1.next_workday()).report("8:00", "1:00", "17:00")
        nt.assert_equal(user_1.next_year(), "2016")

    def test_current_year(self):
        user_1 = user.User(employed_date="2014-12-01")
        nt.assert_equal(user_1.current_year().year, 2014)
        while user_1.next_workday() != "2015-01-02":
            user_1.add_day(user_1.next_workday()).report(
                "8:00", "1:00", "17:00")

        nt.assert_equal(user_1.current_year().year, 2015)

    def test_current_month(self):
        user_1 = user.User(employed_date="2015-01-01")
        nt.assert_is_none(user_1.current_month())
        user_1.add_day(user_1.next_workday()).report("8:00", "1:00", "17:00")
        nt.assert_equal(user_1.current_month().month, 1)
        while user_1.next_workday() != "2015-02-03":
            user_1.add_day(user_1.next_workday()).report(
                "8:00", "1:00", "17:00")

        nt.assert_equal(user_1.current_month().month, 2)

    def test_today(self):
        user_1 = user.User(employed_date="2015-01-01")
        nt.assert_is_none(user_1.today())
        day_1 = user_1.add_day(user_1.next_workday())
        nt.assert_is(user_1.today(), day_1)
        day_1.report_start_time("8:00")
        nt.assert_is(user_1.today(), day_1)
        day_1.report_lunch_duration("1:00")
        nt.assert_is(user_1.today(), day_1)
        day_1.report_end_time("17:00")
        nt.assert_is(user_1.today(), day_1)

        day_2 = user_1.add_day(user_1.next_workday())
        nt.assert_is_not(user_1.today(), day_1)
        nt.assert_is(user_1.today(), day_2)

    def test_calculate_flextime(self):
        user_1 = user.User(employed_date="2014-09-01")
        user_1.add_day("2014-09-01").report("8:00", "0:30", "17:00")
        nt.assert_equal(user_1.calculate_flextime(),
                        datetime.timedelta(minutes=30))

        user_1.add_day("2014-09-02").report("8:00", "1:00", "16:00")
        nt.assert_equal(user_1.calculate_flextime(),
                        datetime.timedelta(minutes=-30))
    
    def test_add_day(self):
        user_1 = user.User(employed_date="2014-09-01")
        day_1 = user_1.add_day("2014-09-01")
        nt.assert_equal(day_1.date, datetime.date(2014, 9, 1))

        user_2 = user.User(employed_date="2014-12-01")
        while user_2.next_workday() != "2015-01-01":
            user_2.add_day(user_2.next_workday()).report(
                "8:00", "1:00", "17:00")

        day_2 = user_2.add_day("2015-01-01")
        nt.assert_equal(day_2.date, datetime.date(2015, 1, 1))

    def test_used_vacation(self):
        user_1 = user.User(payed_vacation=30, vacation_month=1,
                           employed_date="2014-12-01")

        nt.assert_equal(user_1.used_vacation(), 0)
        day_1 = user_1.add_day("2014-12-01")
        day_1.set_type(day.DayType.vacation)
        nt.assert_equal(user_1.used_vacation(), 1)

        while user_1.next_workday() != "2015-01-01":
            user_1.add_day(user_1.next_workday()).report(
                "8:00", "1:00", "17:00")

        day_1 = user_1.add_day("2015-01-01")
        day_1.set_type(day.DayType.vacation)
        nt.assert_equal(user_1.used_vacation(), 2)

    def test_add_year(self):
        user_1 = user.User(employed_date="2014-09-01")
        year_1 = year.Year("2014")
        user_1.add_year(year_1)
        nt.assert_equal(len(user_1.years), 1)
        nt.assert_true(user_1.years[0], year_1)
        year_2 = year.Year("2015")
        nt.assert_raises_regexp(
            errors.YearError,
            "Previous year \(2014\) must be completed first.",
            user_1.add_year,
            year_2)
        
        user_2 = user.User(employed_date="2014-09-01")
        year_3 = year.Year("2014")
        year_3.add_day("2014-01-01")
        nt.assert_raises_regexp(errors.YearError,
                                "Added year can't contain any reported days.",
                                user_2.add_year,
                                year_3)
        
        user_3 = user.User(employed_date="2014-09-01")
        user_3.years[0].add_holiday("2014-01-01", "New Years Day")
        nt.assert_raises_regexp(errors.YearError,
                                "Added year can't contain any reported days.",
                                user_2.add_year,
                                year_3)

    def test_vacation_left(self):
        user_1 = user.User(payed_vacation=30, vacation_month=1,
                           employed_date="2014-01-01")

        user_2 = user.User(payed_vacation=20, vacation_month=7,
                           employed_date="2014-01-01")

        # First day employed
        nt.assert_equal(user_1.vacation_left(date_string="2014-01-01"), 0)
        nt.assert_equal(user_2.vacation_left(date_string="2014-01-01"), 0)

        # The day before user_2 gets half a years vacation days
        nt.assert_equal(user_1.vacation_left(date_string="2014-06-30"), 0)
        nt.assert_equal(user_2.vacation_left(date_string="2014-06-30"), 0)

        # The day user_2 gets half a years vacation days
        nt.assert_equal(user_1.vacation_left(date_string="2014-07-01"), 0)
        nt.assert_equal(user_2.vacation_left(date_string="2014-07-01"), 10)

        # The day before user_1 gets a full years vacation days
        nt.assert_equal(user_1.vacation_left(date_string="2014-12-31"), 0)
        nt.assert_equal(user_2.vacation_left(date_string="2014-12-31"), 10)

        # The day user_1 gets a full years vacation days
        nt.assert_equal(user_1.vacation_left(date_string="2015-01-01"), 30)
        nt.assert_equal(user_2.vacation_left(date_string="2015-01-01"), 10)

        # The day user_2 gets a full years vacation days
        nt.assert_equal(user_1.vacation_left(date_string="2015-07-01"), 30)
        nt.assert_equal(user_2.vacation_left(date_string="2015-07-01"), 30)

        # Without date_string the date for the query is the last worked day
        nt.assert_equal(user_1.vacation_left(), 0)
        nt.assert_equal(user_2.vacation_left(), 0)

        user_1.add_day("2014-01-01").set_type(day.DayType.vacation)
        user_2.add_day("2014-01-01").set_type(day.DayType.vacation)

        nt.assert_equal(user_1.vacation_left(), -1)
        nt.assert_equal(user_2.vacation_left(), -1)

        while user_1.next_workday() != "2015-01-02":
            user_1.add_day(user_1.next_workday()).report(
                "8:00", "1:00", "17:00")
        nt.assert_equal(user_1.vacation_left(), 29)
        user_1.add_day("2015-01-02").set_type(day.DayType.vacation)
        nt.assert_equal(user_1.vacation_left(), 28)

        while user_2.next_workday() != "2015-07-02":
            user_2.add_day(user_2.next_workday()).report(
                "8:00", "1:00", "17:00")
        nt.assert_equal(user_2.vacation_left(), 29)
        user_2.add_day("2015-07-02").set_type(day.DayType.vacation)
        nt.assert_equal(user_2.vacation_left(), 28)

    def test_vacation_left_with_extra_vacation(self):
        user_1 = user.User(employed_date="2015-01-01",
                           vacation_month=4,
                           payed_vacation=30,
                           extra_vacation=30)

        nt.assert_equal(user_1.vacation_left(), 30)
        nt.assert_equal(user_1.vacation_left(date_string="2015-04-01"), 37)
        nt.assert_equal(user_1.vacation_left(date_string="2016-04-01"), 67)
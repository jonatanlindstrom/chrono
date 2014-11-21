# -*- coding: utf-8 -*-

import nose.tools as nt
import os
import tempfile
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

#    def test_next_workday(self):
#        user_1 = user.User(employed_date="2014-09-01")
#        nt.assert_equal(user_1.next_workday(), "2014-09-01")
#        user_2 = user.User(employed_date="2014-11-01")
#        nt.assert_equal(user_2.next_workday(), "2014-11-03")
#
#
#    def test_next_month(self):
#        user_1 = user.User(employed_date="2014-09-01")
#        nt.assert_equal(user_1.next_month(), "2014-09")
#        user_2 = user.User(employed_date="2015-01-01")
#        nt.assert_equal(user_2.next_month(), "2015-01")
#        while user_2.next_workday() != "2015-02-01":
#            user_2.add_day(user_2.next_workday()).report(
#                "8:00", "1:00", "17:00")
#        nt.assert_equal(user_2.next_month(), "2015-02")
#
#    def test_next_year(self):
#        user_1 = user.User(employed_date="2014-12-01")
#        nt.assert_equal(user_1.next_year(), "2015")
#        while user_1.next_workday() != "2015-01-01":
#            user_1.add_day(user_1.next_workday()).report(
#                "8:00", "1:00", "17:00")
#        nt.assert_equal(user_1.next_month(), "2015")
#        user_1.add_day(user_1.next_workday()).report("8:00", "1:00", "17:00")
#        nt.assert_equal(user_1.next_month(), "2016")
#    
    
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
        nt.assert_raises_regex(errors.YearError,
                               "Previous year \(2014\) must be completed first.",
                               user_1.add_year,
                               year_2)
        
        user_2 = user.User(employed_date="2014-09-01")
        year_3 = year.Year("2014")
        year_3.add_day("2014-01-01")
        nt.assert_raises_regex(errors.YearError,
                               "Added year can't contain any reported days.",
                               user_2.add_year,
                               year_3)
        
        user_3 = user.User(employed_date="2014-09-01")
        user_3.years[0].add_holiday("2014-01-01", "New Years Day")
        nt.assert_raises_regex(errors.YearError,
                               "Added year can't contain any reported days.",
                               user_2.add_year,
                               year_3)

    def test_vacation_left(self):
        user_1 = user.User(payed_vacation=30, vacation_month=1,
                           employed_date="2014-01-01")

        user_2 = user.User(payed_vacation=25, vacation_month=4,
                           employed_date="2014-01-01")

        nt.assert_equal(user_1.vacation_left(date_string="2014-01-01"), 0)
        nt.assert_equal(user_2.vacation_left(date_string="2014-01-01"), 0)

        nt.assert_equal(user_1.vacation_left(date_string="2014-12-31"), 0)
        nt.assert_equal(user_2.vacation_left(date_string="2014-12-31"), 0)

        nt.assert_equal(user_1.vacation_left(date_string="2015-01-01"), 30)
        nt.assert_equal(user_2.vacation_left(date_string="2015-01-01"), 0)

        nt.assert_equal(user_1.vacation_left(date_string="2016-04-01"), 60)
        nt.assert_equal(user_2.vacation_left(date_string="2016-04-01"), 50)

        nt.assert_equal(user_1.vacation_left(), 0)
        
        day_1 = user_1.add_day("2014-01-01")
        day_1.set_type(day.DayType.vacation)
        nt.assert_equal(user_1.vacation_left(), -1)

        while user_1.next_workday() != "2015-01-02":
            user_1.add_day(user_1.next_workday()).report("8:00", "1:00", "17:00")
        nt.assert_equal(user_1.vacation_left(), 29)
        day_2 = user_1.add_day("2015-01-02")
        day_2.set_type(day.DayType.vacation)
        nt.assert_equal(user_1.vacation_left(), 28)

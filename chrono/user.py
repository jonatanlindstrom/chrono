# -*- coding: utf-8 -*-

import datetime as dt
import re
import datetime
from chrono import day
from chrono import year
from chrono import errors

class User(object):
    def __init__(self, name="", employed_date=None,
                 employment=100, payed_vacation=0,
                 vacation_month=1):
        self.name = name
        self.years = []
        if employed_date is not None:
            self.employed_date = dt.datetime.strptime(employed_date, "%Y-%m-%d").date()
            self.years.append(year.Year(str(self.employed_date.year), start_date=self.employed_date.isoformat()))
        else:
            self.employed_date = None
        self.employment = employment
        self.flextime = datetime.timedelta()
        self.payed_vacation = payed_vacation
        self.vacation_month = vacation_month
        self.holidays = {}

    def add_day(self, date_string):
        if self.next_workday()[:4] == self.next_year():
            new_year = year.Year(self.next_year())
            for date, name in self.holidays.items():
                new_year.add_holiday(date, name)
            self.years.append(new_year)
        new_day = self.years[-1].add_day(date_string)
        return new_day

    def add_year(self, year_object):
        if len(year_object.months) != 0:
            raise errors.YearError("Added year can't contain any reported days.")
        elif len(self.years) > 0 and year_object.year != self.years[-1].year and not self.years[-1].complete():
            raise errors.YearError("Previous year ({}) must be completed first.".format(self.years[-1].year))
        if len(self.years) > 0 and year_object.year == self.years[-1].year:
            self.years[-1] = year_object
        else:
            year_object.start_date=self.employed_date
            self.years.append(year_object)

    def next_workday(self):
        return self.years[-1].next_workday()

    def next_month(self):
        return self.years[-1].next_month()

    def next_year(self):
        return self.years[-1].next_year()

    def calculate_flextime(self):
        flextime = self.flextime
        for year in self.years:
            flextime += year.calculate_flextime()
        return flextime

    def used_vacation(self, date_string=None):
        return sum([year.used_vacation(date_string=date_string) for year in self.years])

    def vacation_left(self, date_string=None):
        if date_string is None:
            try:
                today = self.years[-1].months[-1].days[-1].date
            except IndexError:
                today = self.employed_date
        else:
            today = dt.datetime.strptime(date_string, "%Y-%m-%d").date()
        first_vacation_month = dt.date(
            self.employed_date.year + (
                self.employed_date.month <= self.vacation_month),
            self.vacation_month,
            1)

        full_vacation_years = max(
            today.year - first_vacation_month.year + (
                today.month >= self.vacation_month),
            0)

        return self.payed_vacation * full_vacation_years - self.used_vacation(date_string=today.isoformat())

    def __str__(self):
        user_string  = """{user.name}
{}
Employment: {user.employment} %
Employed date: {user.employed_date}
Vacation month: {user.vacation_month}""".format("-" * len(self.name), user=self)
        return user_string

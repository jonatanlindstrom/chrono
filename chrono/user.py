# -*- coding: utf-8 -*-

from datetime import datetime
from datetime import timedelta
from datetime import date
from chrono import day
from chrono import year
from chrono import errors

class User(object):
    def __init__(self, name="", employed_date=None, employment=100,
                 payed_vacation=0, vacation_month=1, extra_vacation=0):
        self.name = name
        self.years = []
        if employed_date is not None:
            self.employed_date = datetime.strptime(employed_date, "%Y-%m-%d").date()
            self.years.append(year.Year(str(self.employed_date.year), start_date=self.employed_date.isoformat()))
        else:
            self.employed_date = None
        self.employment = employment
        self.flextime = timedelta()
        self.payed_vacation = payed_vacation
        self.vacation_month = vacation_month
        self.extra_vacation = extra_vacation
        self.holidays = {}

    def add_day(self, date_string):
        """Add a day.
        :type date_string string:  The new date
        :rtype: day.Day
        """
        if self.next_workday()[:4] == self.next_year():
            new_year = year.Year(self.next_year())
            for date, name in self.holidays.items():
                new_year.add_holiday(date, name)
            self.years.append(new_year)
        new_day = self.current_year().add_day(date_string)
        return new_day

    def add_year(self, year_object):
        if len(year_object.months) != 0:
            raise errors.YearError("Added year can't contain any reported days.")
        elif len(self.years) > 0 and year_object.year != self.current_year().year and not self.current_year().complete():
            raise errors.YearError("Previous year ({}) must be completed first.".format(self.current_year().year))
        if len(self.years) > 0 and year_object.year == self.current_year().year:
            self.years[-1] = year_object
        else:
            year_object.start_date=self.employed_date
            self.years.append(year_object)

    def next_workday(self):
        return self.current_year().next_workday()

    def next_month(self):
        return self.current_year().next_month()

    def next_year(self):
        return self.current_year().next_year()

    def current_year(self):
        return self.years[-1]

    def current_month(self):
        if len(self.current_year().months) > 0:
            return self.current_year().months[-1]
        else:
            return None

    def today(self):
        if self.current_month() is None:
            return None
        else:
            return self.current_month().days[-1]

    def calculate_flextime(self):
        flextime = self.flextime
        for year in self.years:
            flextime += year.calculate_flextime()
        return flextime

    def used_vacation(self, date_string=None):
        return sum([year.used_vacation(date_string=date_string)
                    for year in self.years])

    def vacation_left(self, date_string=None):
        if date_string is None:
            if self.today() is None:
                today = self.employed_date
            else:
                today = self.today().date
        else:
            today = datetime.strptime(date_string, "%Y-%m-%d").date()


        first_vacation_month = date(
            self.employed_date.year + (
                self.employed_date.month > self.vacation_month),
            self.vacation_month,
            1)

        years_worked = 0
        if today >= first_vacation_month:
            years_worked +=  (
                (first_vacation_month.month -
                 self.employed_date.month) % 12) / 12

        years_worked += max(
            today.year - first_vacation_month.year - (
                today.month < self.vacation_month),
            0)

        total_vacation_days = (self.payed_vacation * years_worked +
                               self.extra_vacation)

        unused_vacation_days = total_vacation_days - self.used_vacation(
            date_string=today.isoformat())

        return int(unused_vacation_days)

    def all_days(self):
        return [day for year in self.years
                for month in year.months
                for day in month.days]

    def __str__(self):
        user_string  = """{user.name}
{}
Employment: {user.employment} %
Employed date: {user.employed_date}
Vacation month: {user.vacation_month}""".format("-" * len(self.name), user=self)
        return user_string

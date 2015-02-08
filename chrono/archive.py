# -*- coding: utf-8 -*-

import datetime
from chrono import errors


class Archive(object):
    def __init__(self):
        self.months = []

    def calculate_flextime(self):
        flextime = datetime.timedelta()
        for month in self.months:
            flextime += month.calculate_flextime()
        return flextime

    def used_vacation(self):
        used_vacation = 0
        for month in self.months:
            used_vacation += month.used_vacation()
        return used_vacation

    def archive_month(self, month):
        for old_month in self.months:
            if old_month.year == month.year and old_month.month == month.month:
                raise errors.ReportError("Month {}-{} is allready archived."
                                         .format(month.year, month.month))

        date_string = "{}-{:02d}".format(month.year, month.month)
        if self.next_month() != "" and date_string != self.next_month():
            raise errors.ReportError(
                "Months must be archived sequentially. Expected {}, got "
                "{}-{:02d}.".format(
                    self.next_month(), month.year, month.month))

        if not month.complete():
            raise errors.ReportError("Month still has unreported workdays and "
                                     "can't be archived.")
        self.months.append(month)

    def next_month(self):
        if len(self.months) > 0:
            month = self.months[-1].month + 1
            year = self.months[-1].year
            if month > 12:
                month = 1
                year += 1
            new_month = "{}-{:02d}".format(year, month)
        else:
            new_month = ""
        return new_month

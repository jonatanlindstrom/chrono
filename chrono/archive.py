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

    def archive_month(self, month):
        if not month.complete():
            raise errors.ReportError("Month still has unreported workdays and "
                                     "can't be archived.")
        self.months.append(month)

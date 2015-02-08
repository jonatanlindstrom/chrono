# -*- coding: utf-8 -*-

import nose.tools as nt
import datetime
from chrono import day
from chrono import user
from chrono import errors


class TestDay(object):
    def setup(self):
        pass

    def teardown(self):
        pass

    def test_expected_hours(self):
        nt.assert_equal(day.Day("2014-09-01").expected_hours(),
                        datetime.timedelta(hours=8))

        nt.assert_equal(day.Day("2014-09-02").expected_hours(),
                        datetime.timedelta(hours=8))

        nt.assert_equal(day.Day("2014-09-03").expected_hours(),
                        datetime.timedelta(hours=8))

        nt.assert_equal(day.Day("2014-09-04").expected_hours(),
                        datetime.timedelta(hours=8))

        nt.assert_equal(day.Day("2014-09-05").expected_hours(),
                        datetime.timedelta(hours=8))

        nt.assert_equal(day.Day("2014-09-06").expected_hours(),
                        datetime.timedelta())

        nt.assert_equal(day.Day("2014-09-07").expected_hours(),
                        datetime.timedelta())

    def test_bad_date(self):
        nt.assert_raises_regex(errors.BadDateError,
                               "^Bad date string: \"\"$",
                               day.Day,
                               "")

        nt.assert_raises_regex(errors.BadDateError,
                               "^Bad date string: \"25-09-2014\"$",
                               day.Day,
                               "25-09-2014")

        nt.assert_raises_regex(TypeError,
                               "^Given date must be a string.$",
                               day.Day,
                               datetime.date(2014, 9, 25))

        nt.assert_raises(errors.BadDateError, day.Day, "20140925")

    def test_report_start_time(self):
        day_1 = day.Day("2014-09-01")
        nt.assert_equal(day_1.start_time, None)
        day_1.report_start_time("8:00")
        nt.assert_equal(day_1.start_time,
                        datetime.datetime(year=2014, month=9, day=1, hour=8))

        day_2 = day.Day("2014-09-02")
        day_2.report_start_time("8:30")
        nt.assert_equal(
            day_2.start_time,
            datetime.datetime(year=2014, month=9, day=2, hour=8, minute=30))

        nt.assert_raises_regex(
            errors.ReportError,
            "^Date 2014-09-01 allready has a start time.",
            day_1.report_start_time,
            "8.00")

        day_3 = day.Day("2014-09-03")
        nt.assert_raises_regex(
            errors.BadTimeError,
            "^Bad start time: \"8\".",
            day_3.report_start_time,
            "8")

        nt.assert_raises_regex(
            errors.BadTimeError,
            "^Bad start time: \"8.30\".",
            day_3.report_start_time,
            "8.30")

        nt.assert_raises_regex(
            errors.BadTimeError,
            "^Bad start time: \"8:10:14\".",
            day_3.report_start_time,
            "8:10:14")

    def test_report_lunch(self):
        day_1 = day.Day("2014-09-01")
        nt.assert_equal(day_1.lunch_duration, None)
        nt.assert_raises_regex(
            errors.ReportError,
            "^Date 2014-09-01 must have a start time before a lunch duration "
            "can be reported.",
            day_1.report_lunch_duration,
            "1:00")

        day_1.report_start_time("8:00")
        day_1.report_lunch_duration("1:00")
        nt.assert_equal(day_1.lunch_duration, datetime.timedelta(hours=1))

        day_2 = day.Day("2014-09-02")
        day_2.report_start_time("8:10")
        day_2.report_lunch_duration("0:45")
        nt.assert_equal(day_2.lunch_duration, datetime.timedelta(minutes=45))

        nt.assert_raises_regex(
            errors.ReportError,
            "^Date 2014-09-01 allready has a lunch duration.",
            day_1.report_lunch_duration,
            "1:00")

    def test_report_end_time(self):
        day_1 = day.Day("2014-09-01")
        nt.assert_equal(day_1.end_time, None)
        nt.assert_raises_regex(
            errors.ReportError,
            "^Date 2014-09-01 must have a start time before an end time can "
            "be reported.",
            day_1.report_end_time,
            "17:00")

        day_1.report_start_time("8:00")
        nt.assert_raises_regex(
            errors.ReportError,
            "^Date 2014-09-01 must have a lunch duration before an end time "
            "can be reported.",
            day_1.report_end_time,
            "17:00")

        day_1.report_lunch_duration("1:00")
        day_1.report_end_time("17:00")
        nt.assert_equal(day_1.end_time,
                        datetime.datetime(year=2014, month=9, day=1, hour=17))

    def test_report_end_time(self):
        day_1 = day.Day("2014-09-01")
        nt.assert_equal(day_1.deviation, datetime.timedelta())
        day_1.report("8:00", "1:00", "17:00")
        day_1.report_deviation("1:10")
        nt.assert_equal(day_1.deviation,
                        datetime.timedelta(hours=1, minutes=10))

        nt.assert_equal(day_1.worked_hours(),
                        datetime.timedelta(hours=6, minutes=50))
        
        day_2 = day.Day("2014-10-01")
        nt.assert_equal(day_2.deviation, datetime.timedelta())
        day_2.report("8:00", "1:00", "17:00")
        day_2.report_deviation("0")
        nt.assert_equal(day_2.deviation, datetime.timedelta())

        nt.assert_equal(day_2.worked_hours(), datetime.timedelta(hours=8))

    def test_report(self):
        day_1 = day.Day("2014-09-01")
        nt.assert_false(day_1.complete())
        day_1.report("8:00", "1:00", "17:00")
        nt.assert_true(day_1.complete())
        nt.assert_equal(day_1.start_time,
                        datetime.datetime(year=2014, month=9, day=1, hour=8))

        nt.assert_equal(day_1.lunch_duration,
                        datetime.timedelta(hours=1))

        nt.assert_equal(day_1.end_time,
                        datetime.datetime(year=2014, month=9, day=1, hour=17))

        day_2 = day.Day("2014-09-02")
        day_2.report("8:00", "1:00", "16:30")
        nt.assert_equal(
            day_2.end_time,
            datetime.datetime(year=2014, month=9, day=2, hour=16, minute=30))

    def test_bad_end_time(self):
        day_1 = day.Day("2014-09-01")
        day_1.report_start_time("8:00")
        day_1.report_lunch_duration("1:00")
        nt.assert_raises_regex(
            TypeError,
            "^Given end time must be a string.",
            day_1.report_end_time,
            datetime.time(hour=17))

        nt.assert_raises_regex(
            errors.BadTimeError,
            "^Bad end time: \"24:00\"$",
            day_1.report_end_time,
            "24:00")

        nt.assert_raises_regex(
            errors.BadTimeError,
            "^Bad end time: \"17:00:00\"$",
            day_1.report_end_time,
            "17:00:00")

    def test_worked_hours(self):
        day_1 = day.Day("2014-09-01")
        nt.assert_equal(day_1.worked_hours(), datetime.timedelta())

        day_1.report_start_time("8:00")
        day_1.report_lunch_duration("1:00")
        day_1.report_end_time("17:00")
        nt.assert_equal(day_1.worked_hours(), datetime.timedelta(hours=8))

        day_2 = day.Day("2014-09-02")
        day_2.report_start_time("8:10")
        day_2.report_lunch_duration("0:30")
        day_2.report_end_time("16:50")
        nt.assert_equal(day_2.worked_hours(),
                        datetime.timedelta(hours=8, minutes=10))

    def test_worked_hours_custom_end_time(self):
        day_1 = day.Day("2014-09-01")
        nt.assert_raises_regexp(
            errors.ChronoError,
            "Custom end times can only be tried on days in progress.",
            day_1.worked_hours,
            end_time=datetime.datetime(2014, 9, 1, hour=17))

        day_1.report_start_time("8:00")
        nt.assert_equal(
            day_1.worked_hours(
                end_time=datetime.datetime(2014, 9, 1, hour=16, minute=30)),
            datetime.timedelta(hours=8, minutes=30))

        day_1.report_lunch_duration("0:30")
        nt.assert_equal(
            day_1.worked_hours(
                end_time=datetime.datetime(2014, 9, 1, hour=16, minute=30)),
            datetime.timedelta(hours=8))

        day_1.report_deviation("0:45")
        nt.assert_equal(
            day_1.worked_hours(
                end_time=datetime.datetime(2014, 9, 1, hour=16, minute=30)),
            datetime.timedelta(hours=7, minutes=15))

        day_1.report_end_time("17:00")
        nt.assert_raises_regexp(
            errors.ChronoError,
            "Custom end times can only be tried on days in progress.",
            day_1.worked_hours,
            end_time=datetime.datetime(2014, 9, 1, hour=16, minute=30))

    def test_flextime(self):
        day_1 = day.Day("2014-09-01")
        nt.assert_equal(day_1.calculate_flextime(), datetime.timedelta())
                        
        day_1.report_start_time("8:00")
        day_1.report_lunch_duration("0:45")
        day_1.report_end_time("17:00")
        nt.assert_equal(day_1.calculate_flextime(),
                        datetime.timedelta(minutes=15))

        day_2 = day.Day("2014-09-02")
        day_2.report_start_time("9:00")
        day_2.report_lunch_duration("0:30")
        day_2.report_end_time("17:00")
        nt.assert_equal(day_2.calculate_flextime(),
                        datetime.timedelta(minutes=-30))

        day_3 = day.Day("2014-09-03")
        day_3.set_type(day.DayType.sick_day)
        nt.assert_equal(day_3.calculate_flextime(), datetime.timedelta())
        day_3.set_type(day.DayType.vacation)
        nt.assert_equal(day_3.calculate_flextime(), datetime.timedelta())
        day_3.set_type(day.DayType.weekend)
        nt.assert_equal(day_3.calculate_flextime(), datetime.timedelta())
        day_3.set_type(day.DayType.holiday)
        nt.assert_equal(day_3.calculate_flextime(), datetime.timedelta())
        
        day_3.set_type(day.DayType.working_day)
        day_3.report_start_time("8:00")
        day_3.report_lunch_duration("1:01")
        day_3.report_end_time("17:00")
        nt.assert_equal(day_3.calculate_flextime(),
                        datetime.timedelta(minutes=-1))

    def test_day_type(self):
        day_1 = day.Day("2014-09-01")
        day_2 = day.Day("2014-09-06")
        nt.assert_equal(day_1.day_type, day.DayType.working_day)
        nt.assert_equal(day_1.expected_hours(), datetime.timedelta(hours=8))
        nt.assert_equal(day_2.day_type, day.DayType.weekend)
        nt.assert_equal(day_2.expected_hours(), datetime.timedelta(hours=0))
        day_1.set_type(day.DayType.sick_day)    
        nt.assert_equal(day_1.expected_hours(), datetime.timedelta(hours=0))
        day_1.set_type(day.DayType.vacation)    
        nt.assert_equal(day_1.expected_hours(), datetime.timedelta(hours=0))
        day_1.set_type(day.DayType.weekend) 
        nt.assert_equal(day_1.expected_hours(), datetime.timedelta(hours=0))
        day_1.set_type(day.DayType.holiday) 
        nt.assert_equal(day_1.expected_hours(), datetime.timedelta(hours=0))
        day_1.set_type(day.DayType.working_day) 
        nt.assert_equal(day_1.expected_hours(), datetime.timedelta(hours=8))

    def test_day_no_info(self):
        day_1 = day.Day("2014-09-01")
        nt.assert_equal(day_1.comment, None)
        nt.assert_equal(day_1.info, None)
        nt.assert_equal(day_1.get_info(), "")

    def test_day_comment(self):
        day_1 = day.Day("2014-09-01")
        day_1.comment = "Good day."
        nt.assert_equal(day_1.get_info(), "Good day.")

    def test_day_info(self):
        day_1 = day.Day("2014-09-01")
        day_1.info = "A day"
        nt.assert_equal(day_1.get_info(), "A day")

    def test_day_comment_and_info(self):
        day_1 = day.Day("2014-09-01")
        day_1.info = "A day in life"
        day_1.comment = "I read the news today, oh boy!"
        nt.assert_equal(day_1.get_info(),
                        "A day in life. I read the news today, oh boy!")

    def test_day_optional_info_period(self):
        day_1 = day.Day("2014-09-01")
        day_1.info = "A day in life"
        nt.assert_equal(day_1.get_info(), "A day in life")
        day_1.comment = "I read the news today, Oh boy"
        nt.assert_equal(day_1.get_info(),
                        "A day in life. I read the news today, Oh boy.")

        nt.assert_equal(day_1.info, "A day in life")
        nt.assert_equal(day_1.comment, "I read the news today, Oh boy.")

    def test_day_messy_info(self):
        day_1 = day.Day("2014-09-01")
        day_1.info = "  A  day  in  life...     "
        day_1.comment = "    I  read the news today, oh boy "
        nt.assert_equal(day_1.get_info(),
                        "A day in life... I read the news today, oh boy.")

        day_2 = day.Day("2014-09-01")
        day_2.info = "How many roads must a man walk down?\n"
        day_2.comment = """
The answer my friend,
is blowing in the wind.
The answer is blowing in the wind"""

        nt.assert_equal(
            day_2.get_info(),
            "How many roads must a man walk down? The answer my friend, "
            "is blowing in the wind. The answer is blowing in the wind.")

        nt.assert_equal(day_2.info, "How many roads must a man walk down?")
        nt.assert_equal(day_2.comment,
                        "The answer my friend, is blowing in the wind. "
                        "The answer is blowing in the wind.")

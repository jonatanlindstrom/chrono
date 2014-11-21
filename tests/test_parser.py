# -*- coding: utf-8 -*-

import nose.tools as nt
import os
import datetime
import tempfile
from chrono.parser import Parser
from chrono import errors

def save_month_file(string, file_name, folder):
    full_path = os.path.join(folder, file_name)
    with open(full_path, "w") as month_file:
        month_file.write(string)
    return full_path

def save_archive_file(string, folder):
    full_path = os.path.join(folder, "archive.txt")
    with open(full_path, "w") as month_file:
        month_file.write(string)
    return full_path

def save_year_file(string, year, folder):
    full_path = os.path.join(folder, "{}.conf".format(year))
    with open(full_path, "w") as year_file:
        year_file.write(string)
    return full_path


def save_user_file(string, folder):
    full_path = os.path.join(folder, "user.conf")
    with open(full_path, "w") as month_file:
        month_file.write(string)
    return full_path


class TestParserMonthFile(object):
    def setup(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def teardown(self):
        pass

    def test_parse_one_date(self):
        file_parser = Parser()
        file_name = save_month_file(
            "1.\n", "2014-09.txt", self.temp_dir.name)

        month_1 = file_parser.parse_month_file(file_name)
        nt.assert_equal(month_1.year, 2014)
        nt.assert_equal(month_1.month, 9)
        nt.assert_equal(len(month_1.days), 1)

        day_1 = month_1.days[-1]
        nt.assert_equal(day_1.date, datetime.date(2014, 9, 1))
        nt.assert_true(day_1.start_time is None)
        nt.assert_true(day_1.lunch_duration is None)
        nt.assert_true(day_1.end_time is None)
        nt.assert_false(day_1.complete())

    def test_one_partial_date(self):
        file_parser = Parser()
        file_name = save_month_file(
            "1. 8:00\n", "2014-09.txt", self.temp_dir.name)

        month_1 = file_parser.parse_month_file(file_name)
        nt.assert_equal(len(month_1.days), 1)
        day_1 = month_1.days[-1]
        nt.assert_equal(day_1.date, datetime.date(2014, 9, 1))
        nt.assert_equal(day_1.start_time,
                        datetime.datetime(2014, 9, 1, hour=8))

        nt.assert_true(day_1.lunch_duration is None)
        nt.assert_true(day_1.end_time is None)
        nt.assert_false(day_1.complete())

    def test_one_complete_date(self):
        file_parser = Parser()
        file_name = save_month_file(
            "1. 8:00 1:00 17:01\n", "2014-09.txt", self.temp_dir.name)

        month_1 = file_parser.parse_month_file(file_name)
        nt.assert_equal(len(month_1.days), 1)
        day_1 = month_1.days[-1]
        nt.assert_equal(day_1.date, datetime.date(2014, 9, 1))
        nt.assert_equal(day_1.start_time,
                        datetime.datetime(2014, 9, 1, hour=8))

        nt.assert_equal(day_1.lunch_duration,
                        datetime.timedelta(hours=1))

        nt.assert_equal(day_1.end_time,
                        datetime.datetime(2014, 9, 1, hour=17, minute=1))

        nt.assert_true(day_1.complete())
        nt.assert_equal(month_1.calculate_flextime(),
                        datetime.timedelta(minutes=1))

    def test_no_lunch(self):
        file_parser = Parser()
        file_name = save_month_file(
            "1. 8:00 0 12:00\n", "2014-10.txt", self.temp_dir.name)

        month_1 = file_parser.parse_month_file(file_name)
        nt.assert_equal(month_1.days[0].lunch_duration, datetime.timedelta())
        nt.assert_equal(month_1.days[0].worked_hours(),
                        datetime.timedelta(hours=4))

        file_name = save_month_file(
            "1. 9:00 0:00 11:45\n", "2014-09.txt", self.temp_dir.name)

        month_2 = file_parser.parse_month_file(file_name)
        nt.assert_equal(month_2.days[0].lunch_duration, datetime.timedelta())
        nt.assert_equal(month_2.days[0].worked_hours(),
                        datetime.timedelta(hours=2, minutes=45))

    def test_deviation(self):
        file_parser = Parser()
        file_name = save_month_file(
            "1. 8:00 1:00 17:00 0:30\n", "2014-10.txt", self.temp_dir.name)

        month_1 = file_parser.parse_month_file(file_name)
        nt.assert_equal(month_1.days[0].deviation, datetime.timedelta(minutes=30))
        nt.assert_equal(month_1.days[0].worked_hours(),
                        datetime.timedelta(hours=7, minutes=30))

        file_name = save_month_file(
            "1. 9:00 0:45 15:50 1\n", "2014-09.txt", self.temp_dir.name)

        month_2 = file_parser.parse_month_file(file_name)
        nt.assert_equal(month_2.days[0].deviation, datetime.timedelta(hours=1))
        nt.assert_equal(month_2.days[0].worked_hours(),
                        datetime.timedelta(hours=5, minutes=5))

    def test_half_month(self):
        file_parser = Parser()
        file_content = """1. 8:00 1:00 17:00
2. 9:00 0:30 17:45
3. 8:50 0:45 18:00
4. 9:30 1:00 16:55
5. 8:15 1:00 17:10
8. 10:00 0:50 18:05
9. 8:30
"""
        file_name = save_month_file(
            file_content, "2014-09.txt", self.temp_dir.name)

        month_1 = file_parser.parse_month_file(file_name)
        nt.assert_equal(len(month_1.days), 7)
        for day in month_1.days[:-1]:
            nt.assert_true(day.complete)
        nt.assert_false(month_1.days[-1].complete())

    def test_one_and_a_half_month(self):
        file_parser = Parser()
        file_content_1 = """1. 8:00 1:00 17:05
2. 8:00 1:00 17:00
3. 8:00 1:00 17:00
4. 8:00 1:00 17:00
5. 8:00 1:00 17:00
8. 8:00 1:00 17:00
9. 8:00 1:00 17:00
10. 8:00 1:00 17:00
11. 8:00 1:00 17:00
12. 8:00 1:00 17:00
15. 8:00 1:00 17:00
16. 8:00 1:00 17:00
17. 8:00 1:00 17:00
18. 8:00 1:00 17:00
19. 8:00 1:00 17:00
22. 8:00 1:00 17:00
23. 8:00 1:00 17:00
24. 8:00 1:00 17:00
25. 8:00 1:00 17:00
26. 8:00 1:00 17:00
29. 8:00 1:00 17:00
30. 8:00 1:00 17:00"""

        file_content_2 = """1. 8:00 1:00 17:00
2. 8:00 1:00 17:00
3. 8:00 1:00 17:00
6. 8:00 1:00 17:00
7. 8:00 1:00 17:00
8. 8:00 1:00 17:00
9. 8:00 1:00 17:00
10. 8:00 1:00 17:00"""

        file_name_1 = save_month_file(
            file_content_1, "2014-09.txt", self.temp_dir.name)

        file_name_2 = save_month_file(
            file_content_2, "2014-10.txt", self.temp_dir.name)

        month_1 = file_parser.parse_month_file(file_name_1)
        month_2 = file_parser.parse_month_file(file_name_2)
        nt.assert_equal(month_1.month, 9)
        nt.assert_equal(month_2.month, 10)

    def test_sick_days(self):
        file_parser = Parser()
        file_content_1 = """1. 8:00 1:00 17:00
2. 8:00 1:00 17:00"""

        file_name = save_month_file(
            file_content_1, "2014-09.txt", self.temp_dir.name)

        month_1 = file_parser.parse_month_file(file_name)
        nt.assert_equal(month_1.sick_days(), 0)

        file_content_2 = """1. S"""
        file_name = save_month_file(
            file_content_2, "2014-09.txt", self.temp_dir.name)

        month_2 = file_parser.parse_month_file(file_name)
        nt.assert_equal(month_2.sick_days(), 1)
        file_content_3 = """1. 8:00 1:00 17:00
2. S
3. 8:00 1:00 17:00
4. S
5. 8:00 1:00 17:00
8. S"""

        file_name = save_month_file(
            file_content_3, "2014-09.txt", self.temp_dir.name)

        month_3 = file_parser.parse_month_file(file_name)
        nt.assert_equal(month_3.sick_days(), 3)

    def test_vacation(self):
        file_parser = Parser()
        file_content_1 = """1. 8:00 1:00 17:00
2. 8:00 1:00 17:00"""

        file_name = save_month_file(
            file_content_1, "2014-09.txt", self.temp_dir.name)

        month_1 = file_parser.parse_month_file(file_name)
        nt.assert_equal(month_1.used_vacation(), 0)

        file_content_2 = """1. V"""
        file_name = save_month_file(
            file_content_2, "2014-09.txt", self.temp_dir.name)

        month_2 = file_parser.parse_month_file(file_name)
        nt.assert_equal(month_2.used_vacation(), 1)

        file_content_3 = """1. 8:00 1:00 17:00
2. V
3. V
4. 8:00 1:00 17:00
5. 8:00 1:00 17:00
8. V"""

        file_name = save_month_file(
            file_content_3, "2014-09.txt", self.temp_dir.name)

        month_3 = file_parser.parse_month_file(file_name)
        nt.assert_equal(month_3.used_vacation(), 3)

    def test_parse_comments(self):
        file_parser = Parser()
        file_content_1 = """1. 8:00 1:00 17:00
2. 8:00 1:00 14:00 "Went home early because of really good weather"
3. 8:00"""

        file_name = save_month_file(
            file_content_1, "2014-09.txt", self.temp_dir.name)

        month_1 = file_parser.parse_month_file(file_name)
        nt.assert_equal(month_1.days[1].get_info(),
                        "Went home early because of really good weather.")

    def test_parse_comments_single_quote(self):
        file_parser = Parser()
        file_content_1 = """1. 8:00 1:00 17:00
2. 8:00 1:00 14:00 'Went home early because of really good weather'
3. 8:00 0:45 15:00 'Still good weather...'"""
        
        file_name = save_month_file(
            file_content_1, "2014-09.txt", self.temp_dir.name)

        month_1 = file_parser.parse_month_file(file_name)
        nt.assert_equal(month_1.days[1].get_info(),
                        "Went home early because of really good weather.")
        nt.assert_equal(month_1.days[2].get_info(),
                        "Still good weather...")

    def test_unmatched_quote_types(self):
        file_parser = Parser()
        file_content_1 = """1. 8:00 1:00 17:00
2. 8:00 1:00 14:00 "Went home early because of really good weather'"""

        file_name = save_month_file(
            file_content_1, "2014-09.txt", self.temp_dir.name)

        nt.assert_raises_regex(errors.ParseError,
                               "No endquote in comment for date 2014-09-02.",
                               file_parser.parse_month_file,
                               file_name)

        file_content_2 = "1. 8:00 'Bad comment\""
        file_name = save_month_file(
            file_content_2, "2014-09.txt", self.temp_dir.name)

        nt.assert_raises_regex(errors.ParseError,
                               "No endquote in comment for date 2014-09-01.",
                               file_parser.parse_month_file,
                               file_name)

    def test_parse_bad_date(self):
        file_parser = Parser()
        file_content_1 = "1"
        file_name = save_month_file(
            file_content_1, "2014-09.txt", self.temp_dir.name)

        nt.assert_raises_regex(errors.ParseError,
                               "Could not parse date in 2014-09: \"1\"",
                               file_parser.parse_month_file,
                               file_name)

        file_content_2 = "1:"
        file_name = save_month_file(
            file_content_2, "2014-10.txt", self.temp_dir.name)

        nt.assert_raises_regex(errors.ParseError,
                               "Could not parse date in 2014-10: \"1:\"",
                               file_parser.parse_month_file,
                               file_name)

    def test_parse_bad_time(self):
        file_parser = Parser()
        file_name = save_month_file(
            "1. 8.00", "2014-09.txt", self.temp_dir.name)

        nt.assert_raises_regex(
            errors.ParseError,
            "Could not parse start time for date 2014-09-01: \"8.00\"",
            file_parser.parse_month_file,
            file_name)

        file_name = save_month_file(
            "1. 8", "2014-10.txt", self.temp_dir.name)

        nt.assert_raises_regex(
            errors.ParseError,
            "Could not parse start time for date 2014-10-01. Time must be "
            "given in hours and minutes, got \"8\".",
            file_parser.parse_month_file,
            file_name)

        file_name = save_month_file(
            "1. 9", "2014-09.txt", self.temp_dir.name)

        nt.assert_raises_regex(
            errors.ParseError,
            "Could not parse start time for date 2014-09-01. Time must be "
            "given in hours and minutes, got \"9\".",
            file_parser.parse_month_file,
            file_name)
        


class TestParserArchiveFile(object):
    def setup(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def teardown(self):
        pass

    def test_parse_archive_one_month(self):
        file_parser = Parser()
        month_string = "2014-09\n1. 8:00 1:00 17:05"
        for n in (2, 3, 4, 5,
                  8, 9, 10, 11, 12,
                  15, 16, 17, 18, 19,
                  22, 23, 24, 25, 26,
                  29, 30):
            month_string += "\n{}. 8:00 1:00 17:00".format(n)
        file_name = save_archive_file(month_string, self.temp_dir.name)
        archive_1 = file_parser.parse_archive_file(file_name)
        nt.assert_true(len(archive_1.months), 1)
        nt.assert_true(archive_1.months[0].year, 2014)
        nt.assert_true(archive_1.months[0].month, 9)
        nt.assert_true(archive_1.calculate_flextime,
                       datetime.timedelta(minutes=5))

        nt.assert_true(archive_1.next_month, "2014-10")

    def test_parse_archive_multiple_months(self):
        file_parser = Parser()

        archive_string = "2014-11\n3. 8:00 1:00 17:05"
        for n in (4, 5, 6, 7,
                  10, 11, 12, 13, 14,
                  17, 18, 19, 20, 21,
                  24, 25, 26, 27, 28):
            archive_string += "\n{}. 8:00 1:00 17:00".format(n)

        archive_string += "\n\n2014-12\n1. 8:00 1:00 17:05"
        for n in (2, 3, 4, 5,
                  8, 9, 10, 11, 12,
                  15, 16, 17, 18, 19,
                  22, 23, 24, 25, 26,
                  29, 30, 31):
            archive_string += "\n{}. 8:00 1:00 17:00".format(n)

        archive_string += "\n\n2015-01\n1. 8:00 1:00 17:05"
        for n in (2,
                  5, 6, 7, 8, 9,
                  12, 13, 14, 15, 16,
                  19, 20, 21, 22, 23,
                  26, 27, 28, 29, 30):
            archive_string += "\n{}. 8:00 1:00 17:00".format(n)

        file_name = save_archive_file(archive_string, self.temp_dir.name)
        archive_1 = file_parser.parse_archive_file(file_name)
        nt.assert_true(len(archive_1.months), 3)
        nt.assert_true(archive_1.calculate_flextime,
                       datetime.timedelta(minutes=15))

        nt.assert_true(archive_1.next_month, "2015-02")

class TestParserYearConfiguration(object):
    def setup(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def teardown(self):
        pass

    def test_parse_year_configuration(self):
        file_parser = Parser()
        year_string = "2015-01-01: \"New years day\""
        file_name = save_year_file(year_string, "2015", self.temp_dir.name)
        year_1 = file_parser.parse_year_file(file_name)
        nt.assert_equal(year_1.holidays["2015-01"]["2015-01-01"],
                        "New years day")
        
    def test_parse_year_configuration_with_comments(self):
        file_parser = Parser()
        year_string = ("# January\n"
                       "2014-01-01: \"New years day\"\n"
                       "2014-01-06: \"Epiphany\"\n"
                       "\n"
                       "# April\n"
                       "2014-04-18: \"Good friday\"\n"
                       "2014-04-21: \"Easter monday\"")

        file_name = save_year_file(year_string, "2014", self.temp_dir.name)
        year_1 = file_parser.parse_year_file(file_name)
        nt.assert_equal(year_1.holidays["2014-01"]["2014-01-01"],
                        "New years day")

        nt.assert_equal(year_1.holidays["2014-01"]["2014-01-06"],
                        "Epiphany")

        nt.assert_equal(year_1.holidays["2014-04"]["2014-04-18"],
                        "Good friday")

        nt.assert_equal(year_1.holidays["2014-04"]["2014-04-21"],
                        "Easter monday")

class TestParserUserConfiguration(object):
    def setup(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def teardown(self):
        pass

    def test_read_user_file_one_user(self):
        file_parser = Parser()
        user_string = """Name: Jane Doe
Employment: 100 %
Payed vacation: 30
Vacation month: 04
Employed date: 2014-09-01"""

        file_name_1 = save_user_file(user_string, self.temp_dir.name)
        user_1 = file_parser.parse_user_file(file_name_1)
        nt.assert_equal(user_1.name, "Jane Doe")
        nt.assert_equal(user_1.employment, 100)
        nt.assert_equal(user_1.payed_vacation, 30)
        nt.assert_equal(user_1.vacation_month, 4)
        nt.assert_equal(user_1.employed_date,
                        datetime.datetime(year=2014, month=9, day=1).date())

    def test_read_user_file_another_user(self):
        file_parser = Parser()
        user_string = """Name: John Doe
Employment: 75 %
Payed vacation: 25
Vacation month: 1
Employed date: 2012-01-01"""

        file_name_1 = save_user_file(user_string, self.temp_dir.name)
        user_1 = file_parser.parse_user_file(file_name_1)
        nt.assert_equal(user_1.name, "John Doe")
        nt.assert_equal(user_1.employment, 75)
        nt.assert_equal(user_1.payed_vacation, 25)
        nt.assert_equal(user_1.vacation_month, 1)
        nt.assert_equal(user_1.employed_date,
                        datetime.datetime(year=2012, month=1, day=1).date())

    def test_read_messy_user(self):
        file_parser = Parser()
        user_string = """ name :  Sid Vicious
 employment :  20%  
 payed  Vacation :  0  
 vacation  Month :  3
\temployed\tdate\t:\t2013-04-01\t"""

        file_name_1 = save_user_file(user_string, self.temp_dir.name)
        user_1 = file_parser.parse_user_file(file_name_1)
        nt.assert_equal(user_1.name, "Sid Vicious")
        nt.assert_equal(user_1.employment, 20)
        nt.assert_equal(user_1.payed_vacation, 0)
        nt.assert_equal(user_1.vacation_month, 3)
        nt.assert_equal(user_1.employed_date,
                        datetime.datetime(year=2013, month=4, day=1).date())

    def test_bad_user_file(self):
        file_parser = Parser()
        pass

    def test_parse_user_year_month(self):
        file_parser = Parser()
        user_string = """Name: Wayne Doe
Employment: 100 %
Payed vacation: 30
Vacation month: 04
Employed date: 2014-01-01"""

        file_name_1 = save_user_file(user_string, self.temp_dir.name)
        user_1 = file_parser.parse_user_file(file_name_1)

        nt.assert_true(file_parser.user is user_1)

        year_string = ("2014-01-01: \"New years day\"\n"
                       "2014-01-06: \"Epiphany\"")

        file_name_2 = save_year_file(year_string, "2014", self.temp_dir.name)
        year_1 = file_parser.parse_year_file(file_name_2)
        nt.assert_true(file_parser.user.years[0] is year_1)

        month_string = """2. 8:00 1:00 17:00
3. 8:50 0:45 18:00
7. 9:30 1:00 16:55
"""
        file_name_3 = save_month_file(
            month_string, "2014-01.txt", self.temp_dir.name)

        month_1 = file_parser.parse_month_file(file_name_3)
        nt.assert_true(file_parser.user.years[0].months[0] is month_1)
        
# -*- coding: utf-8 -*-

import nose.tools as nt
import os
import datetime
import tempfile
from chrono.parser import Parser
from chrono import errors


class TestParser(object):
    def setup(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def teardown(self):
        pass

    def test_parse_one_date(self):
        file_parser = Parser()

        file_content = "1.\n"
        file_name = os.path.join(self.temp_dir.name, "2014-09.txt")
        with open(file_name, "w") as month_file:
            month_file.write(file_content)

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

        file_content = "1. 8:00\n"
        file_name = os.path.join(self.temp_dir.name, "2014-09.txt")
        with open(file_name, "w") as month_file:
            month_file.write(file_content)

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

        file_content = "1. 8:00 1:00 17:01\n"
        file_name = os.path.join(self.temp_dir.name, "2014-09.txt")
        with open(file_name, "w") as month_file:
            month_file.write(file_content)

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
        file_name = os.path.join(self.temp_dir.name, "2014-09.txt")
        with open(file_name, "w") as month_file:
            month_file.write(file_content)

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

        file_name_1 = os.path.join(self.temp_dir.name, "2014-09.txt")
        file_name_2 = os.path.join(self.temp_dir.name, "2014-10.txt")
        with open(file_name_1, "w") as month_file:
            month_file.write(file_content_1)
        with open(file_name_2, "w") as month_file:
            month_file.write(file_content_2)
        month_1 = file_parser.parse_month_file(file_name_1)
        month_2 = file_parser.parse_month_file(file_name_2)
        nt.assert_equal(month_1.month, 9)
        nt.assert_equal(month_2.month, 10)

    def test_sick_days(self):
        file_parser = Parser()
        file_name = os.path.join(self.temp_dir.name, "2014-09.txt")

        file_content_1 = """1. 8:00 1:00 17:00
2. 8:00 1:00 17:00"""

        with open(file_name, "w") as month_file:
            month_file.write(file_content_1)
        month_1 = file_parser.parse_month_file(file_name)
        nt.assert_equal(month_1.sick_days(), 0)

        file_content_2 = """1. S"""
        with open(file_name, "w") as month_file:
            month_file.write(file_content_2)
        month_2 = file_parser.parse_month_file(file_name)
        nt.assert_equal(month_2.sick_days(), 1)
        file_content_3 = """1. 8:00 1:00 17:00
2. S
3. 8:00 1:00 17:00
4. S
5. 8:00 1:00 17:00
8. S"""

        with open(file_name, "w") as month_file:
            month_file.write(file_content_3)
        month_3 = file_parser.parse_month_file(file_name)
        nt.assert_equal(month_3.sick_days(), 3)

    def test_vacation(self):
        file_parser = Parser()
        file_name = os.path.join(self.temp_dir.name, "2014-09.txt")

        file_content_1 = """1. 8:00 1:00 17:00
2. 8:00 1:00 17:00"""

        with open(file_name, "w") as month_file:
            month_file.write(file_content_1)
        month_1 = file_parser.parse_month_file(file_name)
        nt.assert_equal(month_1.used_vacation(), 0)

        file_content_2 = """1. V"""
        with open(file_name, "w") as month_file:
            month_file.write(file_content_2)
        month_2 = file_parser.parse_month_file(file_name)
        nt.assert_equal(month_2.used_vacation(), 1)

        file_content_3 = """1. 8:00 1:00 17:00
2. V
3. V
4. 8:00 1:00 17:00
5. 8:00 1:00 17:00
8. V"""

        with open(file_name, "w") as month_file:
            month_file.write(file_content_3)
        month_3 = file_parser.parse_month_file(file_name)
        nt.assert_equal(month_3.used_vacation(), 3)

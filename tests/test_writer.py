# -*- coding: utf-8 -*-

import os
import tempfile

import nose.tools as nt

from chrono.writer import write_line


class TestWriter:
    def setup(self):
        self.tempdir = tempfile.TemporaryDirectory()

    def teardown(self):
        pass

    def test_append_line_to_file_that_ends_without_newline(self):
        file_path = self._create_month_file("2015-02.txt",
                                            "2. 8:00 1:00 17:00")

        with open(file_path, 'r') as month_file:
            nt.assert_equal(month_file.read(), "2. 8:00 1:00 17:00")

        write_line(file_path, "3. Row, row, row in line")

        with open(file_path, 'r') as month_file:
            nt.assert_equal(
                month_file.read(),
                "2. 8:00 1:00 17:00\n"
                "3. Row, row, row in line\n")

    def test_append_line_to_file_that_ends_with_newline(self):
        file_path = self._create_month_file("2015-02.txt",
                                            "2. 8:00 1:00 17:00\n")

        with open(file_path, 'r') as month_file:
            nt.assert_equal(month_file.read(), "2. 8:00 1:00 17:00\n")

        write_line(file_path, "3. General I/O stream")

        with open(file_path, 'r') as month_file:
            nt.assert_equal(
                month_file.read(),
                "2. 8:00 1:00 17:00\n"
                "3. General I/O stream\n")

    def test_append_line_to_file_that_ends_with_several_newlines(self):
        file_path = self._create_month_file("2015-02.txt",
                                            "2. 8:00 1:00 17:00\n\n\n\n")

        with open(file_path, 'r') as month_file:
            nt.assert_equal(month_file.read(), "2. 8:00 1:00 17:00\n\n\n\n")

        write_line(file_path, "3. Narrowing, narrowing, narrowing, narrowing")

        with open(file_path, 'r') as month_file:
            nt.assert_equal(
                month_file.read(),
                "2. 8:00 1:00 17:00\n"
                "3. Narrowing, narrowing, narrowing, narrowing\n")

    def test_edit_line_in_file(self):
        file_path = self._create_month_file("2015-02.txt",
                                            "2. 8:00 1:00 17:00\n"
                                            "3. 8:15\n")

        with open(file_path, 'r') as month_file:
            nt.assert_equal(month_file.read(),
                            "2. 8:00 1:00 17:00\n"
                            "3. 8:15\n")

        write_line(file_path, "3. 8:15 0:45")

        with open(file_path, 'r') as month_file:
            nt.assert_equal(
                month_file.read(),
                "2. 8:00 1:00 17:00\n"
                "3. 8:15 0:45\n")

    def test_write_line_to_empty_file(self):
        file_path = self._create_month_file("2015-02.txt", "")

        with open(file_path, 'r') as month_file:
            nt.assert_equal(month_file.read(), "")

        write_line(file_path, "2. 8:00")

        with open(file_path, 'r') as month_file:
            nt.assert_equal(
                month_file.read(),
                "2. 8:00\n")

    def test_write_line_to_new_file(self):
        file_path = os.path.join(self.tempdir.name, "2015-02.txt")

        nt.assert_false(os.path.exists(file_path))

        write_line(file_path, "2. 8:00")

        with open(file_path, 'r') as month_file:
            nt.assert_equal(
                month_file.read(),
                "2. 8:00\n")

    def _create_month_file(self, month, content):
        file_path = os.path.join(self.tempdir.name, "{}.txt".format(month))
        with open(file_path, 'w') as month_file:
            month_file.write(content)
        return file_path
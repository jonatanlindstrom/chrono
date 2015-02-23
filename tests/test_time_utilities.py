# -*- coding: utf-8 -*-

import datetime

import nose.tools as nt

from chrono.time_utilities import pretty_timedelta


class TestTimeHelpers(object):
    def setup(self):
        pass

    def teardown(self):
        pass

    def test_pretty_timedelta_should_return_timestring(self):
        timedelta_1 = datetime.timedelta(hours=1, minutes=23)
        timedelta_2 = datetime.timedelta(hours=-1, minutes=-23)
        timedelta_3 = datetime.timedelta()
        timedelta_4 = None

        nt.assert_equal(pretty_timedelta(timedelta_1), "1:23")
        nt.assert_equal(pretty_timedelta(timedelta_2), "-1:23")
        nt.assert_equal(pretty_timedelta(timedelta_3), "0:00")
        nt.assert_equal(pretty_timedelta(timedelta_4), "")

    def test_pretty_timedelta_should_return_signed_timestring(self):
        positive_timedelta = datetime.timedelta(hours=1, minutes=23)
        negative_timedelta = datetime.timedelta(hours=-1, minutes=-23)
        zero_timedelta = datetime.timedelta()
        none_timedelta = None

        nt.assert_equal(pretty_timedelta(positive_timedelta, signed=True),
                        "+1:23")

        nt.assert_equal(pretty_timedelta(negative_timedelta, signed=True),
                        "-1:23")

        nt.assert_equal(pretty_timedelta(zero_timedelta, signed=True), "0:00")
        nt.assert_equal(pretty_timedelta(none_timedelta, signed=True), "")
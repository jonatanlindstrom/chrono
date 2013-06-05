#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.split(os.path.abspath(__file__))[0], os.pardir)))
    
import nose.tools as nt
import unittest
import chrono

class TestMorphon(object):
    def setup(self):
        pass
        
    def teardown(self):
        pass
        
    def test_make_time(self):
        pass
    
    def test_make_timedelta(self):
        nt.assert_true(chrono.make_timedelta("1:00").seconds, 3600)
        nt.assert_true(chrono.make_timedelta("01:00").seconds, 3600)
        nt.assert_true(chrono.make_timedelta("001:00").seconds, 3600)
        nt.assert_true(chrono.make_timedelta("1").seconds, 3600)
        nt.assert_true(chrono.make_timedelta("01").seconds, 3600)
        nt.assert_true(chrono.make_timedelta("01").seconds, 3600)
        nt.assert_true(chrono.make_timedelta("001").seconds, 3600)
        nt.assert_true(chrono.make_timedelta("1:01").seconds, 3660)
        nt.assert_true(chrono.make_timedelta("1.00").seconds, 3600)
        nt.assert_true(chrono.make_timedelta("01.00").seconds, 3600)
        nt.assert_true(chrono.make_timedelta("001.00").seconds, 3600)
        nt.assert_true(chrono.make_timedelta("1.01").seconds, 3660)
        
        nt.assert_true(chrono.make_timedelta("+1:00").seconds, 3600)
        nt.assert_true(chrono.make_timedelta("+01:00").seconds, 3600)
        nt.assert_true(chrono.make_timedelta("+001:00").seconds, 3600)
        nt.assert_true(chrono.make_timedelta("+1").seconds, 3600)
        nt.assert_true(chrono.make_timedelta("+01").seconds, 3600)
        nt.assert_true(chrono.make_timedelta("+01").seconds, 3600)
        nt.assert_true(chrono.make_timedelta("+001").seconds, 3600)
        nt.assert_true(chrono.make_timedelta("+1:01").seconds, 3660)
        nt.assert_true(chrono.make_timedelta("+1.00").seconds, 3600)
        nt.assert_true(chrono.make_timedelta("+01.00").seconds, 3600)
        nt.assert_true(chrono.make_timedelta("+001.00").seconds, 3600)
        nt.assert_true(chrono.make_timedelta("+1.01").seconds, 3660)
        
        nt.assert_true(chrono.make_timedelta("-1:00").seconds, -3600)
        nt.assert_true(chrono.make_timedelta("-01:00").seconds, -3600)
        nt.assert_true(chrono.make_timedelta("-001:00").seconds, -3600)
        nt.assert_true(chrono.make_timedelta("-1").seconds, -3600)
        nt.assert_true(chrono.make_timedelta("-01").seconds, -3600)
        nt.assert_true(chrono.make_timedelta("-01").seconds, -3600)
        nt.assert_true(chrono.make_timedelta("-001").seconds, -3600)
        nt.assert_true(chrono.make_timedelta("-1:01").seconds, -3660)
        nt.assert_true(chrono.make_timedelta("-1.00").seconds, -3600)
        nt.assert_true(chrono.make_timedelta("-01.00").seconds, -3600)
        nt.assert_true(chrono.make_timedelta("-001.00").seconds, -3600)
        nt.assert_true(chrono.make_timedelta("-1.01").seconds, -3660)
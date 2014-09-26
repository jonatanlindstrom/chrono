# -*- coding: utf-8 -*-

class ChronoError(Exception):
    pass

class BadDateError(ChronoError):
    pass

class BadTimeError(ChronoError):
    pass

class ReportError(ChronoError):
    pass


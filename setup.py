#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(name='chrono',
      version='2014.1.x',
      description="Tool for quick and simple work time tracking using human "
                  "readable text files.",
      author='Jonatan Lindström',
      author_email='jonatanlindstromd@gmail.com',
      install_requires=["docopt"],
      packages=['chrono'],
      entry_points={
              "console_scripts": ["chrono = chrono.chrono:main"]
          }
     )

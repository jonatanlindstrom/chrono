#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup

setup(name='chrono',
      version='1.0b2',
      description="Tool for quick and simple work time tracking using human "
                  "readable text files.",
      author='Jonatan Lindström',
      author_email='jonatanlindstromd@gmail.com',
      install_requires=["docopt", "nose"],
      packages=["chrono"],
      entry_points={
              "console_scripts": ["chrono = chrono.chrono:main"]
      })

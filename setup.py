#!/usr/bin/env python
"""
randio
======
"""
from setuptools import setup

setup(
  name="randio",
  version="0.1.1",
  author='Michel Pelletier',
  author_email='pelletier.michel@yahoo.com',
  description='rtl-sdr radio dongle random number generator',
  packages=['randio'],
  long_description=__doc__,
  license='MIT License',
  classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        ],
)

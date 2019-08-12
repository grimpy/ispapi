#!/usr/bin/env python3
from setuptools import setup

setup(name='ispapi',
      version='0.1',
      description='Collection of ISP API clients with comming cli',
      author='Jo De Boeck',
      author_email='deboeck.jo@gmail.com',
      url='http://github.com/grimpy/ispapi',
      install_requires=['requests'],
      packages=['ispapi'],
      entry_points={'console_scripts': ['ispapi=ispapi.__main__:main']}
      )

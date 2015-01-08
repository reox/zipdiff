from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(name='zipdiff',
      version='0.9-alpha',
      description='Script to diff ZIP Files',
      author='Sebastian Bachmann',
      author_email='hello@reox.at',
      package_dir={'': 'src'},
      packages=[''],
      entry_points = {'console_scripts': ['zipdiff = zipdiff:main']},
      )
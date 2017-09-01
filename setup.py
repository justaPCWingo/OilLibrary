#!/usr/bin/env python
import os
import sys
import fnmatch
import shutil
from subprocess import call

from setuptools import setup, find_packages
from distutils.command.clean import clean
from setuptools import Command
from setuptools.command.test import test as TestCommand

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
pkg_name = 'oil_library'
pkg_version = '1.0.4'


def clean_files(del_db=False):
    src = os.path.join(here, r'oil_library')

    to_rm = []
    for root, _dirnames, filenames in os.walk(src):
        for filename in fnmatch.filter(filenames, '*.pyc'):
            to_rm.append(os.path.join(root, filename))

    to_rm.extend([os.path.join(here, '{0}.egg-info'.format(pkg_name)),
                  os.path.join(here, 'build'),
                  os.path.join(here, 'dist')])
    if del_db:
        to_rm.extend([os.path.join(src, 'OilLib.db')])

    for f in to_rm:
        try:
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)
        except:
            pass

        print "Deleting {0} ..".format(f)


class cleanall(clean):
    description = "cleans files generated by 'develop' and SQL lite DB file"

    def run(self):
        clean.run(self)
        clean_files(del_db=True)


class remake_oil_db(Command):
    '''
    Custom command to reconstruct the oil_library database from flat file
    '''
    description = "remake oil_library SQL lite DB from flat file"
    user_options = user_options = []

    def initialize_options(self):
        """init options"""
        pass

    def finalize_options(self):
        """finalize options"""
        pass

    def run(self):
        to_rm = os.path.join(here, r'oil_library', 'OilLib.db')
        try:
            os.remove(to_rm)
        except OSError as e:
            if e.errno == 2:
                pass
            else:
                raise

        print "Deleting {0} ..".format(to_rm)
        ret = call(os.path.join(sys.prefix, 'bin', 'initialize_OilLibrary_db'))

        if ret == 0:
            print 'OilLibrary database successfully generated from file!'
        else:
            print 'OilLibrary database generation returned: ', ret


class PyTest(TestCommand):
    """So we can run tests with ``setup.py test``"""
    def finalize_options(self):
        TestCommand.finalize_options(self)
        # runs the tests from inside the installed package
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # no idea why it doesn't work to call pytest.main
        # import pytest
        # errno = pytest.main(self.test_args)
        errno = os.system('py.test --pyargs oil_library')
        import sys
        sys.exit(errno)


s = setup(name=pkg_name,
          version=pkg_version,
          description=('{}: {}'.format(pkg_name,
                                       'The NOAA library of oils '
                                       'and their properties.')),
          long_description=README,
          author='ADIOS/GNOME team at NOAA ORR',
          author_email='orr.gnome@noaa.gov',
          url='',
          keywords='adios weathering oilspill modeling',
          packages=find_packages(),
          include_package_data=True,
          package_data={'oil_library': ['OilLib.db',
                                        'OilLib',
                                        'OilLibTest',
                                        'OilLibNorway',
                                        'blacklist_whitelist.txt',
                                        'tests/*.py',
                                        'tests/sample_data/*']},
          cmdclass={'remake_oil_db': remake_oil_db,
                    'cleanall': cleanall,
                    'test': PyTest,
                    },
          entry_points={'console_scripts': [('initialize_OilLibrary_db = '
                                             'oil_library.initializedb'
                                             ':make_db'),
                                            ('diff_import_files = '
                                             'oil_library.scripts.oil_import'
                                             ':diff_import_files_cmd'),
                                            ('add_header_to_import_file = '
                                             'oil_library.scripts.oil_import'
                                             ':add_header_to_csv_cmd'),
                                            ],
                        },
          zip_safe=False,
          )

# make database post install - couldn't call this directly so used
# console script

if 'install' in s.script_args or 'build' in s.script_args:
    print "Calling initialize_OilLibrary_db"
    call("initialize_OilLibrary_db")
elif 'develop' in s.script_args and '--uninstall' not in s.script_args:
    if os.path.exists(os.path.join(here, 'oil_library', 'OilLib.db')):
        print 'OilLibrary database exists - do not remake!'
    else:
        print "Calling initialize_OilLibrary_db"
        ret = call(os.path.join(sys.prefix, 'bin', 'initialize_OilLibrary_db'))

        if ret == 0:
            print 'OilLibrary database successfully generated from file!'
        else:
            print 'OilLibrary database generation returned: ', ret

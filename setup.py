import textwrap
from setuptools import setup


setup(name='fest',
      version='0.1.0',
      author='amancevice',
      author_email='smallweirdnum@gmail.com',
      packages=['fest'],
      url='http://www.smallweirdnumber.com',
      description='Sync Facebook events to other services',
      long_description=textwrap.dedent(
          '''See GitHub_ for documentation.
          .. _GitHub: https://github.com/amancevice/facebook-event-sync'''),
      classifiers=['Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Topic :: Utilities',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python'],
      install_requires=['click >= 6.7.0, < 6.8',
                        'facebook-sdk >= 2.0.0, < 3',
                        'google >= 1.9.3, < 2',
                        'google-api-python-client >= 1.6.4, < 2'],
      entry_points={'console_scripts': ['fest=fest.main:fest']})

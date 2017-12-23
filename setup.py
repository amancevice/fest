import textwrap
from setuptools import setup


setup(name='fest',
      version='0.1.6',
      author='amancevice',
      author_email='smallweirdnum@gmail.com',
      packages=['fest'],
      url='https://github.com/amancevice/fest',
      description='Sync Facebook events to other services',
      long_description=textwrap.dedent(
          '''See GitHub_ for documentation.
          .. _GitHub: https://github.com/amancevice/fest'''),
      install_requires=['click >= 6.7.0, < 6.8',
                        'facebook-sdk >= 2.0.0, < 3',
                        'google >= 1.9.3, < 2',
                        'google-api-python-client >= 1.6.4, < 2'],
      entry_points={'console_scripts': ['fest=fest.main:fest']})

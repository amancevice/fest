import textwrap
from setuptools import setup

GOOGLE = ['google >= 1.9.3, < 2', 'google-api-python-client >= 1.6.4, < 2']
WORDPRESS = ['python-wordpress-xmlrpc >= 2.3.0, < 2.4']
ALL = GOOGLE + WORDPRESS


setup(name='fest',
      version='0.6.1',
      author='amancevice',
      author_email='smallweirdnum@gmail.com',
      packages=['fest'],
      url='https://github.com/amancevice/fest',
      description='Sync Facebook events to other services',
      long_description=textwrap.dedent(
          '''See GitHub_ for documentation.
          .. _GitHub: https://github.com/amancevice/fest'''),
      install_requires=['facebook-sdk >= 2.0.0',
                        'python-dateutil >= 2.6.1'],
      extras_require={'all': ALL,
                      'google': GOOGLE,
                      'wordpress': WORDPRESS})

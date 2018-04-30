from setuptools import setup

GOOGLE = ['google >= 1.9.3',
          'google-api-python-client >= 1.6.4',
          'google-service-http >= 0.0.1']
WORDPRESS = ['python-wordpress-xmlrpc >= 2.3.0']
ALL = GOOGLE + WORDPRESS

setup(name='fest',
      version='2.1.1',
      author='amancevice',
      author_email='smallweirdnum@gmail.com',
      packages=['fest'],
      url='https://github.com/amancevice/fest',
      description='Sync Facebook events to other services',
      long_description='See GitHub_ for documentation.'
                       '.. _GitHub: https://github.com/amancevice/fest',
      install_requires=['facebook-sdk >= 2.0.0',
                        'python-dateutil >= 2.6.1',
                        'pytz >= 2018.3'],
      extras_require={'all': ALL,
                      'google': GOOGLE,
                      'wordpress': WORDPRESS})

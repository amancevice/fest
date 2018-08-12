from setuptools import setup

GOOGLE = [
    'google >= 1.9.3',
    'google-auth >= 1.5.1',
    'google-api-python-client >= 1.6.4']
WORDPRESS = ['python-wordpress-xmlrpc >= 2.3.0']
ALL = GOOGLE + WORDPRESS

setup(
    author='amancevice',
    author_email='smallweirdnum@gmail.com',
    description='Sync Facebook events to other services',
    extras_require={
        'all': ALL,
        'google': GOOGLE,
        'wordpress': WORDPRESS},
    install_requires=[
        'facebook-sdk >= 2.0.0',
        'python-dateutil >= 2.6.1',
        'pytz >= 2018.3'],
    long_description='See GitHub_ for documentation.'
                     '.. _GitHub: https://github.com/amancevice/fest',
    name='fest',
    packages=['fest'],
    setup_requires=['setuptools_scm'],
    url='https://github.com/amancevice/fest',
    use_scm_version=True)

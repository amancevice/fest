from setuptools import setup
from setuptools import find_packages

setup(
    author='amancevice',
    author_email='smallweirdnum@gmail.com',
    description='Sync facebook events to Google Calendar',
    install_requires=[
        'facebook-sdk >= 3.0',
        'google-api-python-client >= 1.6.4',
        'requests >= 2.20',
    ],
    name='fest',
    packages=find_packages(exclude=['tests']),
    setup_requires=['setuptools_scm'],
    url='https://github.com/amancevice/fest',
    use_scm_version=True,
)

from setuptools import setup

setup(
    author='amancevice',
    author_email='smallweirdnum@gmail.com',
    description='Sync facebook events to Google Calendar',
    install_requires=[
        'facebook-sdk >= 3.0.0',
        'google-api-python-client >= 1.6.4',
        'pytz >= 2018.3',
        'requests >= 2.20.0',
    ],
    name='fest',
    packages=['fest'],
    setup_requires=['setuptools_scm'],
    url='https://github.com/amancevice/fest',
    use_scm_version=True,
)

from setuptools import setup
from setuptools import find_packages

with open('README.md', 'r') as readme:
    long_description = readme.read()

setup(
    author='amancevice',
    author_email='smallweirdnum@gmail.com',
    description='Sync facebook events to Google Calendar',
    install_requires=[
        'facebook-sdk >= 3.0',
        'google-api-python-client >= 1.6.4',
        'requests >= 2.20',
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    name='fest',
    packages=find_packages(exclude=['tests']),
    python_requires='>=3.6',
    setup_requires=['setuptools_scm'],
    url='https://github.com/amancevice/fest',
    use_scm_version=True,
)

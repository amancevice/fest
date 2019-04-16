from setuptools import setup
from setuptools import find_packages


def requirements(path):
    with open(path) as req:
        return [x.strip() for x in req.readlines() if not x.startswith('-')]


setup(
    author='amancevice',
    author_email='smallweirdnum@gmail.com',
    description='Sync facebook events to Google Calendar',
    install_requires=requirements('requirements.txt'),
    name='fest',
    packages=find_packages(exclude=['tests']),
    setup_requires=['setuptools_scm'],
    tests_require=requirements('requirements-dev.txt'),
    url='https://github.com/amancevice/fest',
    use_scm_version=True,
)

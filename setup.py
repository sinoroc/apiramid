""" Package setup
"""


import setuptools


PROJECT_NAME = 'apiramid'

SEMVER_MAJOR = 0
SEMVER_MINOR = 0
SEMVER_MAINTENANCE = 0

SEMVER_VERSION = '{major}.{minor}.{maintenance}'.format(
    major=SEMVER_MAJOR,
    minor=SEMVER_MINOR,
    maintenance=SEMVER_MAINTENANCE,
)

INSTALL_REQUIREMENTS = [
    'pyramid',
    'ramlfications',
]

SETUP_REQUIREMENTS = [
    'pytest-runner',
]

TESTS_REQUIREMENTS = [
    'pytest',
    'WebTest',
]


PACKAGES = setuptools.find_packages()


setuptools.setup(
    name=PROJECT_NAME,
    version=SEMVER_VERSION,
    setup_requires=SETUP_REQUIREMENTS,
    install_requires=INSTALL_REQUIREMENTS,
    tests_require=TESTS_REQUIREMENTS,
    packages=PACKAGES,
    include_package_data=True,
)


# EOF

""" Package setup
"""


import setuptools


PACKAGE_NAME = 'apiramid'

SEMVER_MAJOR = 0
SEMVER_MINOR = 0
SEMVER_MAINTENANCE = 0

SEMVER_VERSION = '{major}.{minor}.{maintenance}'.format(
    major=SEMVER_MAJOR,
    minor=SEMVER_MINOR,
    maintenance=SEMVER_MAINTENANCE,
)

REQUIREMENTS = [
    'jsonschema',
    'pyramid',
    'ramlfications',
]

INSTALL_REQUIREMENTS = REQUIREMENTS

TESTS_REQUIREMENTS = REQUIREMENTS + [
    'WebTest',
]

TEST_SUITE = 'tests'

PACKAGES = setuptools.find_packages()


setuptools.setup(
    name=PACKAGE_NAME,
    version=SEMVER_VERSION,
    install_requires=INSTALL_REQUIREMENTS,
    tests_require=TESTS_REQUIREMENTS,
    test_suite=TEST_SUITE,
    packages=PACKAGES,
    include_package_data=True,
)


# EOF

import setuptools


MODULE_NAME = 'apiramid'

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


setuptools.setup(
    name=MODULE_NAME,
    version=SEMVER_VERSION,
    install_requires=INSTALL_REQUIREMENTS,
)

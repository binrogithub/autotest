# pylint: disable=E0611
from distutils.core import setup
import os

try:
    import autotest.common as common
except ImportError:
    import common

from autotest.client.shared import version


def get_package_dir():
    return {'hc_agent': 'hc_agent'}


def get_package_data():
    return {}


def get_packages():
    return ['hc_agent', 'hc_agent.cli']


def get_scripts():
    return []


def run():
    setup(name='autotest',
          description='Autotest framework - hc-agent CLI',
          maintainer='Lucas Meneghel Rodrigues',
          maintainer_email='lmr@redhat.com',
          version=version.get_version(),
          url='http://autotest.github.com',
          package_dir=get_package_dir(),
          package_data=get_package_data(),
          packages=get_packages(),
          scripts=get_scripts())


if __name__ == '__main__':
    run()

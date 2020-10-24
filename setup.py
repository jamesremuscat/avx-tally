from setuptools import setup, find_packages
import re

VERSION = '0.0.1'

setup(
    name='avx-tally',
    version=VERSION,
    description='Tally control devices for AVX',
    author='James Muscat',
    author_email='jamesremuscat@gmail.com',
    url='https://github.com/jamesremuscat/avx-tally',
    packages=['avx-tally'],
    install_requires=["avx>1.3.1", "enum34"],
    extras_require={
        "blinkt": ['blinkt']
    }
)

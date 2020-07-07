#!/usr/bin/env python3

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='appletlib',
    version='1.0.0',
    author='Joerg Mechnich',
    author_email='joerg.mechnich@gmail.com',
    description='Python library providing a QSystemTrayIcon wrapper',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/jmechnich/appletlib',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.6',
)

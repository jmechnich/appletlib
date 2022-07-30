#!/usr/bin/env python3

from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='appletlib',
    author='Joerg Mechnich',
    author_email='joerg.mechnich@gmail.com',
    license='GNU GPLv3',
    description='Python library providing a QSystemTrayIcon wrapper',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/jmechnich/appletlib',
    packages=find_packages(),
    use_scm_version={"local_scheme": "no-local-version"},
    setup_requires=['setuptools_scm'],
    install_requires=["python-daemon", "PyQt5"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.6',
)

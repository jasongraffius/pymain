#!/usr/bin/env python3

from setuptools import setup
import os.path

with open(os.path.join("pymain", "version.py"), "r") as fp:
    __version__ = None
    exec(fp.read())  # Update version from version.py

with open("README.rst", "r") as fp:
    readme_contents = fp.read().strip()

setup(
    name="pymain",
    version=__version__,
    author="Jason Graffius",
    description="A simplified interface for your main function.",
    url="https://github.com/jasongraffius/pymain",
    license="MIT",
    keywords="main arguments option argparse",
    packages=["pymain"],
    long_description=readme_contents,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: Utilities",
    ]
)

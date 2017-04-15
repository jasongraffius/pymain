from setuptools import setup
import os.path

with open(os.path.join("pymain", "version.py"), "r") as fp:
    __version__ = None
    exec(fp.read())  # Update version from version.py

with open("README.md", "r") as fp:
    readme_contents = fp.read().strip()

setup(
    name="pymain",
    version=__version__,
    author="Jason Graffius",
    description="A simplified interface for your main function.",
    license="MIT",
    keywords="main arguments option argparse",
    packages=["pymain"],
    long_description=readme_contents,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
    ]
)

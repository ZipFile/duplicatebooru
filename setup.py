#!/usr/bin/env python

import setuptools


with open("requirements.in") as f:
    requirements = [line.strip() for line in f]


setuptools.setup(
    name="duplicatebooru",
    version="0.0.1",
    description="Detect pixel-identical images",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': ['duplicatebooru=duplicatebooru.cli:main'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Framework :: AsyncIO",
        "Operating System :: POSIX",
    ],
    python_requires='>=3.8',
    install_requires=[
       'aiohttp',
       'aiohttp-jinja2',
       'aioredis',
    ],
)

# coding=utf8
import os
import sys
from setuptools import setup

dir_path = os.path.dirname(os.path.realpath(__file__))

with open("README.md") as f:
    long_description = f.read()

if sys.version_info[0] == 2:
    python2_or_3_deps = ['importlib-metadata==2.1.1', 'decorator==4.4.2']
    python2_or_3_test_deps = ['pytest==4.6.11', 'pytest-mock==1.13.0', 'mock==3.0.5']
elif sys.version_info[0] == 3:
    python2_or_3_deps = []
    python2_or_3_test_deps = ['pytest-mock', 'mock']
    if sys.version_info[1] == 5:
        python2_or_3_test_deps.insert(0, "pytest==6.1.2")
        python2_or_3_test_deps.append('importlib-metadata==2.1.1')
    else:
        python2_or_3_test_deps.insert(0, "pytest")

setup(
    name="adfs-aws-login",
    version="0.2.10",
    description="CLI login to AWS using ADFS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://github.com/NitorCreations/adfs-aws-login",
    download_url="https://github.com/NitorCreations/adfs-aws-login",
    author="Pasi Niemi",
    author_email="pasi.niemi@nitor.com",
    license="Apache 2.0",
    packages=["adfs_aws_login"],
    include_package_data=True,
    scripts=[],
    entry_points={
        "console_scripts": ["adfs-aws-login=adfs_aws_login.cli:adfs_aws_login"],
    },
    setup_requires=["pytest-runner"],
    install_requires=[
        "requests>=2.22.0",
        "threadlocal-aws==0.10",
        "beautifulsoup4>=4.8.1",
        "lxml",
    ] + python2_or_3_deps,
    tests_require=[
        "requests-mock==1.8.0",
        "pytest-cov==2.11.1",
    ] + python2_or_3_test_deps,
    test_suite="tests",
)

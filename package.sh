#!/bin/bash

rm -rf dist/
 
# Create new tar.gz and wheel files
# Only create a universal wheel if py2/py3 compatible and no C extensions
python setup.py sdist bdist_wheel --universal
 
# Sign the distributions
gpg --detach-sign -a dist/*

#!/bin/bash
rm -rf build dist
python setup.py sdist bdist_wheel
VERSION=$1
gpg -o dist/adfs_aws_login-${VERSION}-py2.py3-none-any.whl.asc -b dist/adfs_aws_login-${VERSION}-py2.py3-none-any.whl
gpg -o dist/adfs-aws-login-${VERSION}.tar.gz.asc -b dist/adfs-aws-login-${VERSION}.tar.gz

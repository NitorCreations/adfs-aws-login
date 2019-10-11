#!/bin/bash
rm -rf build dist
python setup.py sdist bdist_wheel
VERSION=$1
keybase pgp sign -d -i dist/adfs_aws_login-${VERSION}-py2.py3-none-any.whl -o dist/adfs_aws_login-${VERSION}-py2.py3-none-any.whl.asc
keybase pgp sign -d -i dist/adfs-aws-login-${VERSION}.tar.gz -o dist/adfs-aws-login-${VERSION}.tar.gz.asc

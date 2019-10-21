# coding=utf8
from setuptools import setup
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
with open(dir_path + '/README.md', 'r') as f:
    README = ''.join(f.readlines())

setup(name='adfs-aws-login',
      version='0.1.3',
      description='CLI login to AWS using ADFS',
      long_description=README,
      long_description_content_type='text/markdown',
      url='http://github.com/NitorCreations/adfs-aws-login',
      download_url='https://github.com/NitorCreations/adfs-aws-login',
      author='Pasi Niemi',
      author_email='pasi.niemi@nitor.com',
      license='Apache 2.0',
      packages=['adfs_aws_login'],
      include_package_data=True,
      scripts=[],
      entry_points={
          'console_scripts': ['adfs-aws-login=adfs_aws_login.cli:adfs_aws_login'],
      },
      setup_requires=['pytest-runner'],
      install_requires=[
          'requests==2.22.0',
          'threadlocal-aws==0.6',
          'beautifulsoup4==4.8.1'],
      tests_require=[
          'pytest==4.6.5',
          'pytest-mock==1.10.4',
          'pytest-cov==2.7.1',
          'requests-mock==1.6.0',
          'pytest-runner',
          'mock==3.0.5'
      ],
      test_suite='tests')

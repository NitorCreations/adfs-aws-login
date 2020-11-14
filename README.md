# Log in to AWS using ADFS

The aim for this is to create a general purpose CLI ADFS login with a limited set of trusted dependencies.

[![Codeship Status for NitorCreations/adfs-aws-login](https://app.codeship.com/projects/39311e10-ce2c-0137-479b-3eefd6c4e4a3/status?branch=master)](https://app.codeship.com/projects/368815)

## Installation

It's [available on PyPI](https://pypi.org/project/adfs-aws-login/). Install by running `pip install adfs-aws-login`.

## Run

The executable is called `adfs-aws-login`. Log in with default profile by simply running `adfs-aws-login` or specify a profile with `adfs-aws-login --profile [profile]`. 

See `adfs-aws-login -h` for more options.

If the environment variable `ADFS_DEFAULT_PASSWORD` is defined, that will be used as the password.

## Configure

Configure the profiles in `$HOME/.aws/config`. Following is an example with all supported configuration keys (and a few aws default ones):
```
[profile example]
region=us-east-1
output=json
adfs_login_url=https://login.example.com/adfs/ls/IdpInitiatedSignOn.aspx?loginToRp=urn:amazon:webservices
adfs_default_username=test.user@example.com
adfs_role_arn=arn:aws:iam::1234567890:role/DeployRole
adfs_session_duration=8
```

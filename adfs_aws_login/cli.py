import sys
from os import environ
from getpass import getpass
from adfs_aws_login import credentials, saml
from adfs_aws_login.conf import init
from threadlocal_aws import region
from threadlocal_aws.clients import sts

try:
    input = raw_input
except NameError:
    pass

def adfs_aws_login():
    conf = init()
    username = None
    # Get the federated credentials from the user
    if not conf.NO_PROMPT:
        sys.stdout.write("Username [" + conf.DEFAULT_USERNAME + "]: ")
        username = input()
    if not username:
        if conf.DEFAULT_USERNAME:
            username = conf.DEFAULT_USERNAME
        else:
            print("Need to give username")
            sys.exit(1)
    if "ADFS_DEFAULT_PASSWORD" in environ and environ["ADFS_DEFAULT_PASSWORD"]:
        password = environ["ADFS_DEFAULT_PASSWORD"]
    password = getpass()

    try:
        assertion, awsroles = saml.get_saml_assertion(username, password, conf)
    except saml.SamlException as e:
        print(e.message)
        sys.exit(1)

    # Overwrite and delete the credential variables, just for safety
    username = '##############################################'
    password = '##############################################'
    del username
    del password

    if not conf.NO_PROMPT:
        # If I have more than one role, ask the user which one they want,
        # otherwise just proceed
        if len(awsroles) > 1:
            i = 0
            print("Please choose the role you would like to assume:")
            for awsrole in awsroles:
                print('[', i, ']: ', awsrole.split(',')[0])
                i += 1
            sys.stdout.write("Selection: ")
            selectedroleindex = input()

            # Basic sanity check of input
            if int(selectedroleindex) > (len(awsroles) - 1):
                print("You selected an invalid role index, please try again")
                sys.exit(1)

            role_arn = awsroles[int(selectedroleindex)].split(',')[0]
            principal_arn = awsroles[int(selectedroleindex)].split(',')[1]
        else:
            role_arn = awsroles[0].split(',')[0]
            principal_arn = awsroles[0].split(',')[1]
    else:
        for awsrole in awsroles:
            if awsrole.startswith(conf.ROLE_ARN + ","):
                role_arn = conf.ROLE_ARN
                principal_arn = awsrole.split(',')[1]
    
    if not role_arn:
        print("No valid role found in assertions")
        sys.exit(3)
    # Use the assertion to get an AWS STS token using Assume Role with SAML
    token = sts().assume_role_with_saml(RoleArn=role_arn, PrincipalArn=principal_arn,
                                        SAMLAssertion=assertion, DurationSeconds=conf.DURATION)
    credentials.write(token, conf.PROFILE)

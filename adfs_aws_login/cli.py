import sys

import requests
import base64
import logging
import xml.etree.ElementTree as ET
import re
from getpass import getpass
from adfs_aws_login import conf, credentials
from threadlocal_aws import region
from threadlocal_aws.clients import sts
from bs4 import BeautifulSoup


try:
    # For Python 3.5 and later
    from urllib.parse import urlunparse
    from urllib.parse import urlparse
except ImportError:
    input = raw_input
    from urlparse import urlunparse # noqa: F401
    from urlparse import urlparse   # noqa: F401

def adfs_aws_login():
    conf.init()

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
    password = getpass()
    print ''

    # Initiate session handler
    session = requests.Session()

    # Programmatically get the SAML assertion
    # Opens the initial IdP url and follows all of the HTTP302 redirects, and
    # gets the resulting login page
    formresponse = session.get(conf.ADFS_LOGIN_URL, verify=True)
    # Capture the idpauthformsubmiturl, which is the final url after all the 302s
    idpauthformsubmiturl = formresponse.url

    # Parse the response and extract all the necessary values
    # in order to build a dictionary of all of the form values the IdP expects
    formsoup = BeautifulSoup(formresponse.text.decode('utf8'),"lxml")
    payload = {}

    for inputtag in formsoup.find_all(re.compile('(INPUT|input)')):
        name = inputtag.get('name','')
        value = inputtag.get('value','')
        if "user" in name.lower():
            #Make an educated guess that this is the right field for the username
            payload[name] = username
        elif "email" in name.lower():
            #Some IdPs also label the username field as 'email'
            payload[name] = username
        elif "pass" in name.lower():
            #Make an educated guess that this is the right field for the password
            payload[name] = password
        else:
            #Simply populate the parameter with the existing value (picks up hidden fields in the login form)
            payload[name] = value

    # Some IdPs don't explicitly set a form action, but if one is set we should
    # build the idpauthformsubmiturl by combining the scheme and hostname 
    # from the entry url with the form action target
    # If the action tag doesn't exist, we just stick with the 
    # idpauthformsubmiturl above
    for inputtag in formsoup.find_all(re.compile('(FORM|form)')):
        action = inputtag.get('action')
        loginid = inputtag.get('id')
        if (action and loginid == "loginForm"):
            parsedurl = urlparse(conf.ADFS_LOGIN_URL)
            idpauthformsubmiturl = parsedurl.scheme + "://" + parsedurl.netloc + action

    # Performs the submission of the IdP login form with the above post data
    response = session.post(
        idpauthformsubmiturl, data=payload, verify=True)

    # Overwrite and delete the credential variables, just for safety
    username = '##############################################'
    password = '##############################################'
    del username
    del password

    # Decode the response and extract the SAML assertion
    soup = BeautifulSoup(response.text.decode('utf8'),"lxml")
    assertion = ''

    # Look for the SAMLResponse attribute of the input tag (determined by
    # analyzing the debug print lines above)
    for inputtag in soup.find_all('input'):
        if(inputtag.get('name') == 'SAMLResponse'):
            assertion = inputtag.get('value')

    # Better error handling is required for production use.
    if (assertion == ''):
        print 'Response did not contain a valid SAML assertion'
        sys.exit(2)

    # Parse the returned assertion and extract the authorized roles
    awsroles = []
    root = ET.fromstring(base64.b64decode(assertion))
    for saml2attribute in root.iter('{urn:oasis:names:tc:SAML:2.0:assertion}Attribute'):
        if (saml2attribute.get('Name') == 'https://aws.amazon.com/SAML/Attributes/Role'):
            for saml2attributevalue in saml2attribute.iter('{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue'):
                awsroles.append(saml2attributevalue.text)

    # Note the format of the attribute value should be role_arn,principal_arn
    # but lots of blogs list it as principal_arn,role_arn so let's reverse
    # them if needed
    for awsrole in awsroles:
        chunks = awsrole.split(',')
        if'saml-provider' in chunks[0]:
            newawsrole = chunks[1] + ',' + chunks[0]
            index = awsroles.index(awsrole)
            awsroles.insert(index, newawsrole)
            awsroles.remove(awsrole)

    if not conf.NO_PROMPT:
        # If I have more than one role, ask the user which one they want,
        # otherwise just proceed
        print("")
        if len(awsroles) > 1:
            i = 0
            print "Please choose the role you would like to assume:"
            for awsrole in awsroles:
                print('[', i, ']: ', awsrole.split(',')[0])
                i += 1
            sys.stdout.write("Selection: ")
            selectedroleindex = input()

            # Basic sanity check of input
            if int(selectedroleindex) > (len(awsroles) - 1):
                print 'You selected an invalid role index, please try again'
                sys.exit(0)

            role_arn = awsroles[int(selectedroleindex)].split(',')[0]
            principal_arn = awsroles[int(selectedroleindex)].split(',')[1]
        else:
            role_arn = awsroles[0].split(',')[0]
            principal_arn = awsroles[0].split(',')[1]
    else:
        for awsrole in awsroles:
            if awsrole.startswith(conf.ROLE_ARN + ","):
                role_arn = conf.ROLE_ARN
                principal_arn = awsroles.split(',')[1]
    
    if not role_arn:
        print("No valid role found in assertions")
        sys.exit(3)

    # Use the assertion to get an AWS STS token using Assume Role with SAML
    token = sts().assume_role_with_saml(RoleArn=role_arn, PrincipalArn=principal_arn, SAMLAssertion=assertion)
    credentials.write(token)

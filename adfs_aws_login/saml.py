import base64
import re
import requests
from bs4 import BeautifulSoup
from adfs_aws_login import conf
import xml.etree.ElementTree as ET

try:
    # For Python 3.5 and later
    from urllib.parse import urlunparse
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlunparse  # noqa: F401
    from urlparse import urlparse  # noqa: F401


def _to_str(data):
    ret = data
    decode_method = getattr(data, "decode", None)
    if callable(decode_method):
        try:
            ret = data.decode()
        except:
            ret = _to_str(base64.b64encode(data))
    return str(ret)


class SamlException(Exception):
    pass


def get_saml_assertion(username, password, conf):
    # Initiate session handler
    session = requests.Session()

    # Programmatically get the SAML assertion
    # Opens the initial IdP url and follows all of the HTTP302 redirects, and
    # gets the resulting login page
    formresponse = session.get(conf.ADFS_LOGIN_URL, verify=True)
    # Raise an error if this failed:
    formresponse.raise_for_status()

    # Capture the idpauthformsubmiturl, which is the final url after all the 302s
    idpauthformsubmiturl = formresponse.url

    # Parse the response and extract all the necessary values
    # in order to build a dictionary of all of the form values the IdP expects
    formsoup = BeautifulSoup(_to_str(formresponse.text), "lxml")
    payload = {}

    for inputtag in formsoup.find_all(re.compile("(INPUT|input)")):
        name = inputtag.get("name", "")
        value = inputtag.get("value", "")
        if "user" in name.lower():
            # Make an educated guess that this is the right field for the username
            payload[name] = username
        elif "email" in name.lower():
            # Some IdPs also label the username field as 'email'
            payload[name] = username
        elif "pass" in name.lower():
            # Make an educated guess that this is the right field for the password
            payload[name] = password
        else:
            # Simply populate the parameter with the existing value (picks up hidden fields in the login form)
            payload[name] = value

    # Some IdPs don't explicitly set a form action, but if one is set we should
    # build the idpauthformsubmiturl by combining the scheme and hostname
    # from the entry url with the form action target
    # If the action tag doesn't exist, we just stick with the
    # idpauthformsubmiturl above
    for inputtag in formsoup.find_all(re.compile("(FORM|form)")):
        action = inputtag.get("action")
        loginid = inputtag.get("id")
        if action and loginid == "loginForm":
            parsedurl = urlparse(conf.ADFS_LOGIN_URL)
            idpauthformsubmiturl = parsedurl.scheme + "://" + parsedurl.netloc + action

    # Performs the submission of the IdP login form with the above post data
    response = session.post(idpauthformsubmiturl, data=payload, verify=True)
    # Raise an error if this failed:
    response.raise_for_status()

    # Overwrite and delete the credential variables, just for safety
    username = "##############################################"
    password = "##############################################"
    del username
    del password

    # Decode the response and extract the SAML assertion
    soup = BeautifulSoup(_to_str(response.text), "lxml")
    assertion = ""

    # Look for the SAMLResponse attribute of the input tag (determined by
    # analyzing the debug print lines above)
    for inputtag in soup.find_all("input"):
        if inputtag.get("name") == "SAMLResponse":
            assertion = inputtag.get("value")

    # Better error handling is required for production use.
    if assertion == "":
        raise SamlException("Response did not contain a valid SAML assertion")

    # Parse the returned assertion and extract the authorized roles
    awsroles = []
    root = ET.fromstring(base64.b64decode(assertion))
    for saml2attribute in root.iter("{urn:oasis:names:tc:SAML:2.0:assertion}Attribute"):
        if saml2attribute.get("Name") == "https://aws.amazon.com/SAML/Attributes/Role":
            for saml2attributevalue in saml2attribute.iter(
                "{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue"
            ):
                awsroles.append(saml2attributevalue.text)

    for awsrole in awsroles:
        chunks = awsrole.split(",")
        if "saml-provider" in chunks[0]:
            newawsrole = chunks[1] + "," + chunks[0]
            index = awsroles.index(awsrole)
            awsroles.insert(index, newawsrole)
            awsroles.remove(awsrole)

    return assertion, awsroles
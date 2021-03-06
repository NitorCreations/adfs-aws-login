from os.path import expanduser

try:
    # For Python 3.5 and later
    import configparser
except ImportError:
    # Fall back to Python 2
    import ConfigParser as configparser


def write(new_creds, profile):
    aws_creds = configparser.ConfigParser()
    home = expanduser("~")
    creds_file = home + "/.aws/credentials"
    aws_creds.read(creds_file)

    if not aws_creds.has_section(profile):
        aws_creds.add_section(profile)

    c = new_creds["Credentials"]
    aws_creds.set(profile, "aws_access_key_id", c["AccessKeyId"])
    aws_creds.set(profile, "aws_secret_access_key", c["SecretAccessKey"])
    aws_creds.set(profile, "aws_session_token", c["SessionToken"])
    aws_creds.set(profile, "aws_session_expiration", c["Expiration"].isoformat())

    with open(creds_file, "w") as configfile:
        aws_creds.write(configfile)

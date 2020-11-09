from os import getenv
from os.path import expanduser, join
import sys
import argparse
import json
import logging

try:
    # For Python 3.5 and later
    import configparser
except ImportError:
    # Fall back to Python 2
    import ConfigParser as configparser  # noqa: F401


CALLBACK_SERVER_TIMEOUT = 30

def init():
    aws_config = configparser.ConfigParser()
    home = expanduser('~')
    aws_config.read(join(home, '.aws', 'config'))
    try:
        my_conf = Config(_parse_args(), aws_config)
    except ConfigExeption as ex:
        print(ex)
        sys.exit(1)

    return my_conf


def _fail_message(missing_config, profile):
    return "No value for required configuration parameter {} in profile {}.".format(missing_config, profile)


def _parse_args():
    parser = argparse.ArgumentParser(description='AWS ADFS Login')
    parser.add_argument('-p', '--profile', type=str, nargs='?', default=getenv('AWS_PROFILE', 'default'),
                        help='AWS profile name to log in with')
    parser.add_argument('-u', '--user', type=str, nargs='?', default=getenv('ADFS_USER', ''),
                        help='Username to log in with')
    parser.add_argument('-n', '--no-prompt', action="store_true", help="Do not prompt for username and AWS role (need to be set in config in this case)")
    parser.add_argument('-d', '--duration', type=int, help="Duration of the session in hours. Defaults to 1.")
    parser.add_argument('-r', '--role', help="The AWS IAM role ARN to assume")
    return parser.parse_args()


class ConfigExeption(Exception):
    pass

class Config:
    def __init__(self, args, aws_config):
        self.PROFILE = args.profile
        self.DEFAULT_USERNAME = args.user
        self.CONFIG_PROFILE = args.profile
        self.NO_PROMPT = args.no_prompt
        self.ROLE_ARN = args.role
        if args.duration:
            self.DURATION = args.duration * 3600
        else:
            self.DURATION = None
        if self.CONFIG_PROFILE != 'default':
            self.CONFIG_PROFILE = 'profile {}'.format(self.PROFILE)
        if not aws_config.has_section(self.CONFIG_PROFILE):
            raise ConfigExeption("Couldn't find configuration for profile: {}".format(self.PROFILE))

        config_section = aws_config[self.CONFIG_PROFILE]
        self.ADFS_LOGIN_URL = config_section.get('adfs_login_url', None)
        if self.ADFS_LOGIN_URL is None:
            raise ConfigExeption(_fail_message('adfs_login_url', self.PROFILE))
        if not self.ROLE_ARN:
            self.ROLE_ARN = config_section.get('adfs_role_arn', None)
        if not self.DEFAULT_USERNAME:
            self.DEFAULT_USERNAME = config_section.get('adfs_default_username', None)
        if not self.DURATION:
            conf_duration = config_section.get('adfs_session_duration', "")
            if conf_duration.isdigit():
                self.DURATION = int(conf_duration) * 3600
        if not self.DURATION:
            self.DURATION = 3600

    def __str__(self):
        return json.dumps({"adfs_url": self.ADFS_LOGIN_URL, "profile": self.PROFILE,
            "username": self.DEFAULT_USERNAME, "profile": self.PROFILE,
            "conf_profile": self.CONFIG_PROFILE, "no-prompt": self.NO_PROMPT,
            "role-arn": self.ROLE_ARN}, indent=2)


if __name__ == "__main__":
    init()

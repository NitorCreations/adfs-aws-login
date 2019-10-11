from os import getenv
from os.path import expanduser, join
import sys
import argparse

try:
    # For Python 3.5 and later
    import configparser
except ImportError:
    # Fall back to Python 2
    import ConfigParser as configparser  # noqa: F401


CALLBACK_SERVER_TIMEOUT = 30
ADFS_LOGIN_URL = None
ROLE_ARN = None
PROFILE = None
CONFIG_PROFILE = None
DEFAULT_USERNAME = None
NO_PROMPT = False


def init():
    global ADFS_LOGIN_URL, ROLE_ARN, PROFILE, CONFIG_PROFILE, DEFAULT_USERNAME
    _init_from_args(_parse_args())
    aws_config = configparser.ConfigParser()
    home = expanduser('~')
    aws_config.read(join(home, '.aws', 'config'))

    if not aws_config.has_section(CONFIG_PROFILE):
        print("Couldn't find configuration for profile: {}".format(PROFILE))
        sys.exit(1)

    config_section = aws_config[CONFIG_PROFILE]
    ADFS_LOGIN_URL = config_section.get('adfs_login_url', None)
    ROLE_ARN = config_section.get('adfs_role_arn', None)
    if not DEFAULT_USERNAME:
        DEFAULT_USERNAME = config_section.get('adfs_default_username', None)

    if ADFS_LOGIN_URL is None:
        _fail('adfs_login_url', PROFILE)


def _fail(missing_config, profile):
    print("No value for required configuration parameter {} in profile {}.".format(missing_config, profile))
    sys.exit(1)


def _parse_args():
    parser = argparse.ArgumentParser(description='AWS ADFS Login')
    parser.add_argument('-p', '--profile', type=str, nargs='?', default=getenv('AWS_PROFILE', 'default'),
                        help='AWS profile name to log in with')
    parser.add_argument('-u', '--user', type=str, nargs='?', default=getenv('ADFS_USER', ''),
                        help='Username to log in with')
    parser.add_argument('-n', '--no-prompt', action="store_true", help="Do not prompt for username and AWS role (need to be set in config in this case)")
    return parser.parse_args()


def _init_from_args(args):
    global PROFILE, CONFIG_PROFILE, DEFAULT_USERNAME

    PROFILE = args.profile
    DEFAULT_USERNAME = args.user
    CONFIG_PROFILE = args.profile
    NO_PROMPT = args.no_prompt
    if CONFIG_PROFILE != 'default':
        CONFIG_PROFILE = 'profile {}'.format(PROFILE)


if __name__ == "__main__":
    init()

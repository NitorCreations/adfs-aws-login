import adfs_aws_login.conf as config
import adfs_aws_login.credentials as credentials
import pytest
from datetime import datetime

try:
    # For Python 3.5 and later
    import configparser
except ImportError:
    # Fall back to Python 2
    import ConfigParser as configparser  # noqa: F401

assume_role_response = {
    "Credentials": {
        "AccessKeyId": "testkeytestkeytestkey",
        "SecretAccessKey": "testsecret",
        "SessionToken": "testtoken",
        "Expiration": datetime.now(),
    }
}
test_profile = "test_write"


def test_new_profile(
    aws_config_read_patched,
    aws_config_write_patched,
    aws_config_add_section_patched,
    aws_config_set_patched,
    aws_config_has_section_patched,
    aws_file_open,
):
    credentials.write(assume_role_response, test_profile)

    _verify(
        aws_config_read_patched,
        aws_config_write_patched,
        aws_config_add_section_patched,
        aws_config_set_patched,
        aws_config_not_has_section_patched,
        aws_file_open,
    )
    aws_config_add_section_patched.assert_not_called()


def test_update_profile(
    aws_config_read_patched,
    aws_config_write_patched,
    aws_config_add_section_patched,
    aws_config_set_patched,
    aws_config_not_has_section_patched,
    aws_file_open,
):
    credentials.write(assume_role_response, test_profile)

    _verify(
        aws_config_read_patched,
        aws_config_write_patched,
        aws_config_add_section_patched,
        aws_config_set_patched,
        aws_config_not_has_section_patched,
        aws_file_open,
    )
    aws_config_add_section_patched.assert_called_with(test_profile)


def _verify(
    aws_config_read_patched,
    aws_config_write_patched,
    aws_config_add_section_patched,
    aws_config_set_patched,
    aws_config_has_section_patched,
    aws_file_open,
):
    assert aws_config_write_patched.call_count == 1
    assert aws_config_read_patched.call_count == 1
    aws_config_set_patched.assert_any_call(
        test_profile,
        "aws_access_key_id",
        assume_role_response["Credentials"]["AccessKeyId"],
    )
    aws_config_set_patched.assert_any_call(
        test_profile,
        "aws_session_expiration",
        assume_role_response["Credentials"]["Expiration"].isoformat(),
    )
    aws_config_set_patched.assert_any_call(
        test_profile,
        "aws_session_token",
        assume_role_response["Credentials"]["SessionToken"],
    )
    aws_config_set_patched.assert_any_call(
        test_profile,
        "aws_secret_access_key",
        assume_role_response["Credentials"]["SecretAccessKey"],
    )


@pytest.fixture
def aws_config_read_patched(mocker):
    return mocker.patch("configparser.ConfigParser.read", return_value=True)


@pytest.fixture
def aws_config_has_section_patched(mocker):
    return mocker.patch("configparser.ConfigParser.has_section", return_value=True)


@pytest.fixture
def aws_config_not_has_section_patched(mocker):
    return mocker.patch("configparser.ConfigParser.has_section", return_value=False)


@pytest.fixture
def aws_config_add_section_patched(mocker):
    return mocker.patch("configparser.ConfigParser.add_section", return_value=None)


@pytest.fixture
def aws_config_set_patched(mocker):
    return mocker.patch("configparser.ConfigParser.set", return_value=None)


@pytest.fixture
def aws_config_write_patched(mocker):
    return mocker.patch("configparser.ConfigParser.write", return_value=None)


@pytest.fixture
def aws_file_open(mocker):
    return mocker.patch("adfs_aws_login.credentials.open", mocker.mock_open())

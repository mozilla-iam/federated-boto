import pwd
import os
import logging
from xml.etree import ElementTree

import requests


logger = logging.getLogger(__name__)


def get_credentials(bearer_token, role_arn):
    """Exchange a bearer token and IAM Role ARN for AWS API keys

    :param bearer_token: OpenID Connect ID token provided by IdP
    :param role_arn: AWS IAM Role ARN of the role to assume
    :return: dict : Dictionary of credential information
    """
    local_username = pwd.getpwuid(os.getuid())[0]
    role_session_name = 'federated-aws-cli-{}'.format(local_username)
    sts_url = "https://sts.amazonaws.com/"
    parameters = {
        'Action': 'AssumeRoleWithWebIdentity',
        'RoleArn': role_arn,
        'RoleSessionName': role_session_name,
        'WebIdentityToken': bearer_token,
        'Version': '2011-06-15'
    }

    # Call the STS API
    resp = requests.get(url=sts_url, params=parameters)
    if resp.status_code != requests.codes.ok:
        logger.error('AWS STS Call failed {} : {}'.format(resp.status_code, resp.text))
        return False

    logger.debug('STS Call Response headers : {}'.format(resp.headers))
    logger.debug('STS Call Response : {}'.format(resp.text))

    root = ElementTree.fromstring(resp.content)
    # Create a dictionary of the children of
    # AssumeRoleWithWebIdentityResult/Credentials and their values
    credentials = dict([(x.tag.split('}', 1)[-1], x.text) for x in root.find(
        './sts:AssumeRoleWithWebIdentityResult/sts:Credentials',
        {'sts': 'https://sts.amazonaws.com/doc/2011-06-15/'})])

    return credentials

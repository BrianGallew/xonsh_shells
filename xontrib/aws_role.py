'''Secure and use AWS role-based session credentials'''
from getpass import getpass
import time
import builtins
from subprocess import run
import boto3
from botocore.exceptions import ParamValidationError
from natural.date import compress
import xonsh
from xontrib.shared_cache import shared_cache

#########
# AWS fanciness
from xontrib.powerline import register_sec, Section, pl_build_prompt

_env = builtins.__xonsh_env__
_EXPIRATION = 'Expiration'
_ACCESSKEYID = 'AccessKeyId'
_SECRETACCESSKEY = 'SecretAccessKey'
_SESSIONTOKEN = 'SessionToken'
_DURATION = 43200


def _get_session_token():
    '''Get role-based access credentials'''
    boto3.setup_default_session(profile_name=_env['AWS_PROFILE'])
    sts_identity = boto3.client('sts').get_caller_identity()
    aws_username = sts_identity['Arn'].split("/")[-1]
    mfa_device = boto3.client('iam').list_mfa_devices(
        UserName=aws_username)['MFADevices']
    session_token = dict()
    try:
        if mfa_device:
            mfa_code = getpass("MFA Code: ")
            print()
            session_token = boto3.client('sts').get_session_token(
                DurationSeconds=_DURATION,
                SerialNumber=mfa_device[0]['SerialNumber'],
                TokenCode=mfa_code)['Credentials']
        else:
            session_token = boto3.client('sts').get_session_token(
                DurationSeconds=_DURATION)['Credentials']
    except ParamValidationError as e:
        print('LOSER!', e)
        return False

    return session_token


def _get_and_show_session_token():
    session_token = _get_session_token()
    if session_token:
        print(f'''
[default]
aws_access_key_id = {session_token["AccessKeyId"]}
aws_secret_access_key = {session_token["SecretAccessKey"]}
aws_session_token = {session_token["SessionToken"]}
region = {boto3._get_default_session().region_name}
''')


def get_aws_credentials(user_name, role):
    '''Get role-based access credentials'''
    boto3.setup_default_session(profile_name=_env['AWS_PROFILE'])
    sts_identity = boto3.client('sts').get_caller_identity()
    aws_username = sts_identity['Arn'].split("/")[-1]
    mfa_device = boto3.client('iam').list_mfa_devices(
        UserName=aws_username)['MFADevices']
    role_aws_token = dict()
    try:
        if mfa_device:
            mfa_code = getpass("MFA Code: ")
            print()
            role_aws_token = boto3.client('sts').assume_role(
                DurationSeconds=_DURATION,
                RoleArn=role,
                RoleSessionName=user_name,
                SerialNumber=mfa_device[0]['SerialNumber'],
                TokenCode=mfa_code)['Credentials']
        else:
            role_aws_token = boto3.client('sts').assume_role(
                DurationSeconds=_DURATION,
                RoleArn=role,
                RoleSessionName=user_name)['Credentials']
    except ParamValidationError:
        expand_roles()
        return False

    role_aws_token['Expiration'] = time.time() + _DURATION
    return role_aws_token


def get_policy_list(iam_client, group_name):
    '''Get the list of policies associated with the group'''
    policy_list = []

    group_policies_inline = iam_client.list_group_policies(
        GroupName=group_name)
    for policy_name in group_policies_inline['PolicyNames']:
        policy_list.append(iam_client.get_group_policy(
            GroupName=group_name, PolicyName=policy_name)['PolicyDocument'])

    group_policies_attached = iam_client.list_attached_group_policies(
        GroupName=group_name)
    for policy_arn in [x['PolicyArn'] for x in group_policies_attached['AttachedPolicies']]:
        policy_info = iam_client.get_policy(PolicyArn=policy_arn)
        policy_doc = iam_client.get_policy_version(
            PolicyArn=policy_arn,
            VersionId=policy_info['Policy']['DefaultVersionId'])['PolicyVersion']['Document']
        policy_list.append(policy_doc)
    return policy_list


def expand_roles():
    'Talk to AWS for role information'
    iam_client = boto3.client('iam')

    user_id = boto3.client('sts').get_caller_identity().get(
        'Arn').split("/")[1]

    user_groups = iam_client.list_groups_for_user(UserName=user_id)

    user_assume_roles = {
        'user': user_id,
        'accounts': dict()
    }

    for group_name in [x['GroupName'] for x in user_groups['Groups']]:
        for policy_info in get_policy_list(iam_client, group_name):
            if not isinstance(policy_info['Statement'], list):
                policy_info['Statement'] = [policy_info['Statement']]

            for statement in policy_info['Statement']:
                if 'Action' not in statement:
                    continue
                # this in test will work whether Action is a list or a string.
                if 'sts:AssumeRole' in statement['Action']:
                    for x in statement['Resource']:
                        parts = x.split(":")
                        account_id = parts[4]
                        role = (parts[5].split("/"))[1]
                        user_assume_roles['accounts'].setdefault(
                            account_id, dict())[role] = x
    if user_assume_roles['accounts']:
        list_roles(user_assume_roles)
    else:
        print("No roles defined for", user_id)
    return


def list_roles(role_list):
    '''Display the user's roles'''
    print(f"\n{role_list['user']}: ")
    for account in role_list['accounts']:

        print(f"  account {account}: ")

        for role in role_list['accounts'][account]:
            print(f"    {role}")
        print()


@register_sec
def aws():
    try:
        if _env['AWS_PROFILE'] in _env['AWS_SESSIONS']:
            remaining = _env['AWS_SESSIONS'][_env['AWS_PROFILE']
                                             ][_EXPIRATION] - int(time.time())
            if remaining > 300:
                return Section('AWS: %s(%s) ' % (_env['AWS_PROFILE'], compress(remaining)),
                               'GREEN', '#333')
            else:
                return Section('AWS: %s(%s) ' % (_env['AWS_PROFILE'], compress(remaining)),
                               'GREEN', 'RED')
        return Section('AWS: %s ' % _env['AWS_PROFILE'], 'GREEN', '#333')
    except Exception as e:
        return Section('', 'WHITE', '#333')


_env['PL_RPROMPT'] = 'aws>history>time'
pl_build_prompt()


def _aws_role(args):
    'Call with PROFILE and ROLE'
    if len(args) != 2:
        print("Error: call aws_role with two arguments: PROFILE and ROLE")
        print("You called it with", args)
        return
    _env['AWS_PROFILE'] = args[0]
    _env['AWS_ROLE'] = args[1]
    if ('AWS_SESSIONS' not in _env) or (_env['AWS_SESSIONS'] is None):
        _env['AWS_SESSIONS'] = dict()
    if args[0] in _env['AWS_SESSIONS']:
        token = _env['AWS_SESSIONS'][_env['AWS_PROFILE']]
    else:
        token = dict()
        token[_EXPIRATION] = 0
    if token[_EXPIRATION] - int(time.time()) < 300:
        for key in ['AWS_SESSION_TOKEN', 'AWS_SECRET_ACCESS_KEY', 'AWS_ACCESS_KEY_ID']:
            if key in builtins.__xonsh_env__:
                del builtins.__xonsh_env__[key]
        token = get_aws_credentials(_env['USER'], _env['AWS_ROLE'])
        if not token:
            return
        _env['AWS_SESSIONS'][_env['AWS_PROFILE']] = token
    _env['AWS_ACCESS_KEY_ID'] = token[_ACCESSKEYID]
    _env['AWS_SECRET_ACCESS_KEY'] = token[_SECRETACCESSKEY]
    _env['AWS_SESSION_TOKEN'] = token[_SESSIONTOKEN]
    return


shared_cache.share_value(['AWS_SESSIONS'])
aliases['aws_role'] = _aws_role  # noqa: F821
aliases['new_session'] = _get_and_show_session_token  # noqa: F821


@xonsh.tools.uncapturable
def _knife_command(args, stdin=None, stdout=None, stderr=None):
    '''Make "knife" an alias that automatically uses the correct
    configuration based on your AWS profile.'''
    arg_list = list(args)
    try:
        arg_list.insert(1,
                        f'{_env["HOME"]}/.chef/knife-{_env["AWS_PROFILE"]}.rb')
        arg_list.insert(1, '-c')
    except KeyError:
        print("running knife with whatever 'knife block' is configured for")
    arg_list.insert(0, '/usr/local/bin/knife')
    run(arg_list, stdin=stdin, stdout=stdout, stderr=stderr)


aliases['knife'] = _knife_command  # noqa: F821

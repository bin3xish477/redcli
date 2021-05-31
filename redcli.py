#!/usr/bin/env python3

# third party
from typer import Typer, echo, Argument, Option
from typing import List, Optional
from rich.console import Console
from tabulate import tabulate
from boto3.session import Session
from botocore.exceptions import ProfileNotFound

# internal
from providers.aws.sts import Sts
from providers.aws.iam import Iam
from providers.aws.ec2 import Ec2
from providers.aws.s3 import S3
from providers.aws.imds import Imds

# globals
aws_app = Typer()
gcp_app = Typer()
redcli_app = Typer()
redcli_app.add_typer(aws_app, name="aws")
redcli_app.add_typer(gcp_app, name="gcp")
console = Console()
tbl_fmt = "fancy_grid"

__version__ = "1.0"
__author__  = "binexisHATT"


# *********************************
# *********** HELPERS *************
# *********************************

# [START _create_session]
def _create_session(profile: str):
    try:
        session = Session(profile_name=profile)
    except ProfileNotFound:
        console.log("> Profile was not found.. ([red]ERROR[/red])")
        console.log("> Try specifying a different profile name.. ([yellow]ACTION[/yellow])")
        exit()
    return session
# [END _create_session]

# *********************************
# ************* MAIN **************
# *********************************

# ************** AWS **************
# [START _user_data_rev_shell]
def _user_data_rev_shell(session: Session, ami_id: str, instance_type: str, rhost: str, rport: int):
    console.log("> Running `user-data-rev-shell` command.. ([blink purple]OK[/blink purple])")
    Ec2(session, console).user_data_rev_shell(ami_id, instance_type, rhost, rport)
# [END _user_data_rev_shell]

# [START _launch_ec2_with_instance_profile]
def _launch_ec2_with_instance_profile(
    session: Session, key_name: str, ami_id: str, instance_profile_arn: str,
    security_group_ids: list, subnet_id: str, instance_type: str
    ):
    console.log("> Running `launch-ec2-with-instance-profile` command.. ([blink purple]OK[/blink purple])")
    Ec2(session, console).launch_ec2_with_instance_profile(
        key_name=key_name, ami_id=ami_id, security_group_ids=security_group_ids,
        instance_profile_arn=instance_profile_arn, instance_type=instance_type,
        subnet_id=subnet_id
    )
# [END _launch_ec2_with_instance_profile]

# [START _get_instance_profiles]
def _get_instance_profiles(session: Session):
    console.log("> Running `get-instance-profiles` command.. ([blink purple]OK[/blink purple])")
    instance_profiles = Ec2(session, console).get_instance_profiles()
    if not instance_profiles:
        console.print("> No instance profiles were found.. ([yellow]INFO[/yellow])")
        return
    instance_profile_tbl = tabulate(instance_profiles, headers=["InstanceID", "InstanceProfileArn"], tablefmt=tbl_fmt)
    console.print(instance_profile_tbl)
# [END _get_instance_profiles]

# [START _list_permissions]
def _list_iam_permissions(session: Session):
    console.log("> Running `ls-perms` command.. ([blink purple]OK[/blink purple])")
    policies = Iam(session, console).get_policies()
    if not policies:
        console.print("> No policies were found.. ([yellow]INFO[/yellow])")
    policy_tbl = tabulate(policies, headers=["PolicyName", "PolicyARN"], tablefmt=tbl_fmt)
    console.print(policy_tbl)
# [END _list_permissions]

# [START _list_buckets]
def _list_buckets(session: Session):
    console.log("> Running `ls-buckets` command.. ([blink purple]OK[/blink purple])")
    buckets = S3(session, console).list_buckets()
    if not buckets:
        console.print("> No buckets were found.. ([yellow]INFO[/yellow])")
    bucket_tbl = tabulate(buckets, headers=["BucketName", "CreationDate"], tablefmt=tbl_fmt)
    console.print(bucket_tbl)
# [END _list_buckets]

# [START _dump_buckets]
def _dump_buckets(session: Session, bucket: str):
    console.log("> Running `dump-buckets` command.. ([blink purple]OK[/blink purple])")
    S3(session, console).dump_buckets(bucket)
# [END _dump_buckets]

# [START _get_instance_creds]
def _get_instance_creds(instance_ip: str, key_file: str, user: str, new_profile_name: str):
    console.log("> Running `get-instance-creds` command.. ([blink purple]OK[/blink purple])")
    Imds(console).get_security_credentials(instance_ip, key_file, user, new_profile_name)
# [END _get_instance_creds]

# [START _get_user_data]
def _get_user_data(instance_ip: str, key_file: str, user: str):
    console.log("> Running `get-user-data` command.. ([blink purple]OK[/blink purple])")
    Imds(console).get_user_data(instance_ip, key_file, user)
# [END _get_user_data]

# [START _mount_snapshot]
def _mount_snapshot():
    console.log("> Running `mount_snapshot` command.. ([blink purple]OK[/blink purple])")
# [END _mount_snapshot]

# [START _get_security_groups]
def _get_security_groups(session: Session):
    console.log("> Running `get-security-groups` command.. ([blink purple]OK[/blink purple])")
    Ec2(session, console).get_security_groups()
# [END _get_security_groups]

# [START _list_s3_acls]
def _list_s3_acls(session: Session, bucket: str):
    console.log("> Running `list-s3-acls` command.. ([blink purple]OK[/blink purple])")
    S3(session, console).list_acls(bucket)
# [END _list_s3_acls]

# [START _whoami]
def _whoami(session: Session):
    console.log("> Running `whoami` command.. ([blink purple]OK[/blink purple])")
    ident = Sts(session).whoami()
    keys = ["UserId", "Account", "Arn"]
    values = ident.values()
    ident_tbl = tabulate(zip(keys, values), headers=["Key", "Value"], tablefmt=tbl_fmt)
    console.print(ident_tbl)
# [END _whoami]


# ************** GCP **************
def _get_instance_token():
    pass


# *********************************
# ******* REDCLI COMMANDS *********
# *********************************

# ************** AWS **************
# [START user_data_rev_shell]
@aws_app.command()
def user_data_rev_shell(
        ami_id: str = Option("ami-00a208c7cdba991ea", help="The ID of the AMI"),
        instance_type: str = Option("t2.micro", help="The instance type to create"),
        rhost: str = Argument(..., help="The remote attacker's IP address|URI"),
        rport: int=Option(7777, help="The remote attacker's listening port"),
        region: str = Argument(..., help="AWS region"),
        profile: str = Argument(..., help="AWS profile")
    ):
    """
    Obtain a reverse shell via user-data script
    """
    _user_data_rev_shell(_create_session(profile), ami_id, instance_type, rhost, rport)
# [END user_data_rev_shell]

# [START launch_ec2_with_instance_profile]
@aws_app.command()
def launch_ec2_with_instance_profile(
        instance_profile_arn: str = Argument(..., help="Instance profile ARN"),
        ami_id: str = Option("ami-00a208c7cdba991ea", help="The ID of the AMI"),
        key_name: str = Option("awsred-ssh", help="Name of the key pair to create"),
        instance_type: str = Option("t2.micro", help="The instance type to create"),
        subnet_id: str = Option("", help="The subnet ID to launch the Ec2 in"),
        security_group_ids: Optional[List[str]] = Option(None, help="The security group ID's to attach to the new instance"), 
        region: str = Argument(..., help="AWS region"),
        profile: str = Argument(..., help="AWS profile")
    ):
    """
    Launch an Ec2 instance and attach specified instance profile
    """
    _launch_ec2_with_instance_profile(
        _create_session(profile), key_name, ami_id, instance_profile_arn,
        security_group_ids, subnet_id, instance_type
    )
# [END launch_ec2_with_instance_profile]

# [START get_instance_profiles]
@aws_app.command()
def get_instance_profiles(
        region: str = Argument(..., help="AWS region"),
        profile: str = Argument(..., help="AWS profile")
    ):
    """
    List all instance profiles
    """
    _get_instance_profiles(_create_session(profile))
# [END get_instance_profiles]

# [START list_permissions]
@aws_app.command()
def list_iam_permissions(profile: str = Argument(..., help="AWS profile")):
    """
    List permissions associated with profile
    """
    _list_iam_permissions(_create_session(profile))
# [END list_permissions]

# [START list_buckets]
@aws_app.command()
def list_buckets(profile: str = Argument(...,help="AWS profile")):
    """
    List all S3 buckets if allowed
    """
    _list_buckets(_create_session(profile))
# [END list_buckets]

# [START dump_buckets]
@aws_app.command()
def dump_buckets(
        bucket: str = Option("", help="Speicific S3 bucket to dump"),
        region: str = Argument(..., help="AWS region"),
        profile: str = Argument(..., help="AWS profile"),
    ):
    """
    Dump content for all S3 buckets
    """
    _dump_buckets(_create_session(profile), bucket)
# [END dump_buckets]

# [START get_instance_creds]
@aws_app.command()
def get_instance_creds(
        instance_ip: str = Argument(..., help="IP address or Public DNS name of Ec2 instance"),
        key_file: str = Argument(..., help="SSH key file for Ec2 instance"),
        user: str = Argument("ec2-user", help="The SSH user associated with key file"),
        new_profile_name: str = Option("awsred", help="New AWS profile name to create with credentials")
    ):
    """
    Get instance credentials via Instance Metadata Server (v1|v2)
    """
    _get_instance_creds(instance_ip, key_file, user, new_profile_name)
# [END get_instance_creds]

# [START get_user_data]
@aws_app.command()
def get_user_data(
    instance_ip: str = Argument(..., help="IP address of Ec2 instance"),
    key_file: str = Argument(..., help="SSH key file for Ec2 instance"),
    user: str = Argument(..., help="The SSH user associated with key file")
    ):
    """
    Get an instances user-data script
    """
    _get_user_data(instance_ip, key_file, user)
# [END get_user_data]

# [START get_security_groups]
@aws_app.command()
def get_security_groups(
        region: str = Argument(..., help="AWS region"),
        profile: str = Argument(..., help="AWS profile") 
    ):
    """
    List all Ec2 instances security groups
    """
    _get_security_groups(_create_session(profile))
# [END get_security_groups]

# [START list_s3_acls]
@aws_app.command()
def list_s3_acls(
        bucket: str = Option("", help="Speicific S3 bucket to dump"),
        region: str = Argument(..., help="AWS region"),
        profile: str = Argument(..., help="AWS profile") 
    ):
    """
    List all S3 bucket Access Control Lists (ACLs)
    """
    _list_s3_acls(_create_session(profile), bucket)
# [END list_s3_acls]

# [START whoami]
@aws_app.command()
def whoami(profile: str = Argument(..., help="AWS profile")):
    """
    Get profile identity
    """
    _whoami(_create_session(profile))
# [END whoami]

# ************** GCP ****************
@gcp_app.command()
def get_instance_token(self):
    pass


if __name__ == "__main__":
    console.print(f"""[red]\

 ██▀███  ▓█████ ▓█████▄  ▄████▄   ██▓     ██▓
▓██ ▒ ██▒▓█   ▀ ▒██▀ ██▌▒██▀ ▀█  ▓██▒    ▓██▒
▓██ ░▄█ ▒▒███   ░██   █▌▒▓█    ▄ ▒██░    ▒██▒
▒██▀▀█▄  ▒▓█  ▄ ░▓█▄   ▌▒▓▓▄ ▄██▒▒██░    ░██░
░██▓ ▒██▒░▒████▒░▒████▓ ▒ ▓███▀ ░░██████▒░██░
░ ▒▓ ░▒▓░░░ ▒░ ░ ▒▒▓  ▒ ░ ░▒ ▒  ░░ ▒░▓  ░░▓  
  ░▒ ░ ▒░ ░ ░  ░ ░ ▒  ▒   ░  ▒   ░ ░ ▒  ░ ▒ ░
  ░░   ░    ░    ░ ░  ░ ░          ░ ░    ▒ ░
   ░        ░  ░   ░    ░ ░          ░  ░ ░  
                 ░      ░[/red]
                          Author:  [bold yellow]{__author__}[/bold yellow]
                          Version: [bold green]{__version__}[/bold green]
    """)
    redcli_app()

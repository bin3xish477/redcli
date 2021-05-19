#!/usr/bin/env python3

# third party
from typer import Typer, echo, Argument, Option
from typing import List, Optional
from rich.console import Console
from tabulate import tabulate
from boto3.session import Session
from botocore.exceptions import ProfileNotFound

# internal
from services.sts import Sts
from services.iam import Iam
from services.ec2 import Ec2
from services.s3 import S3
from services.eks import Eks
from services.imds import Imds

# globals
app = Typer()
console = Console()
tbl_fmt = "fancy_grid"


# *********************************
# *********** HELPERS *************
# *********************************

def _create_session(profile: str):
    try:
        session = Session(profile_name=profile)
    except ProfileNotFound:
        console.log("Profile was not found.. ([red]ERROR[/red])")
        console.log("Try specifying a different profile name.. ([yellow]ACTION[/yellow])")
        exit()
    return session


# *********************************
# ************* MAIN **************
# *********************************

def _user_data_rev_shell(session: Session, rhost: str, rport: int):
    console.log("Running `user-data-rev-shell` command.. ([blink purple]OK[/blink purple])")

def _launch_ec2_with_instance_profile(
    session: Session, key_name: str, ami_id: str, instance_profile_arn: str,
    security_group_ids: list, subnet_id: str, instance_type: str
    ):
    console.log("Running `launch-ec2-with-instance-profile` command.. ([blink purple]OK[/blink purple])")
    Ec2(session, console).launch_ec2_with_instance_profile(
        key_name=key_name, ami_id=ami_id, security_group_ids=security_group_ids,
        instance_profile_arn=instance_profile_arn, instance_type=instance_type,
        subnet_id=subnet_id
    )

def _get_instance_profiles(session: Session):
    console.log("Running `get-instance-profiles` command.. ([blink purple]OK[/blink purple])")
    instance_profiles = Ec2(session, console).get_instance_profiles()
    if not instance_profiles:
        console.print("No instance profiles were found.. ([yellow]INFO[/yellow])")
        return
    instance_profile_tbl = tabulate(instance_profiles, headers=["InstanceID", "InstanceProfileArn"], tablefmt=tbl_fmt)
    console.print(instance_profile_tbl)

def _list_permissions(session: Session):
    console.log("Running `ls-perms` command.. ([blink purple]OK[/blink purple])")
    policies = Iam(session, console).get_policies()
    if not policies:
        console.print("No policies were found.. ([yellow]INFO[/yellow])")
    policy_tbl = tabulate(policies, headers=["PolicyName", "PolicyARN"], tablefmt=tbl_fmt)
    console.print(policy_tbl)

def _list_buckets(session: Session):
    console.log("Running `ls-buckets` command.. ([blink purple]OK[/blink purple])")
    buckets = S3(session, console).list_buckets()
    if not buckets:
        console.print("No buckets were found.. ([yellow]INFO[/yellow])")
    bucket_tbl = tabulate(buckets, headers=["BucketName", "CreationDate"], tablefmt=tbl_fmt)
    console.print(bucket_tbl)

def _dump_buckets(session: Session, bucket: str):
    console.log("Running `dump-bucket` command.. ([blink purple]OK[/blink purple])")
    if bucket == "":
        all = True
    S3(session, console).dump_buckets(bucket)

def _add_user_to_group(session: Session, username: str):
    console.log("Running `add-user-to-group` command.. ([blink purple]OK[/blink purple])")
    # use list-groups to list groups and have user select group
    # create user and then add to specified group
    pass

def _get_instance_creds(
    session: Session, instance_ip: str, key_file: str, user: str, v1: bool):
    console.log("Running `get-instance-creds` command.. ([blink purple]OK[/blink purple])")
    Imds(session, console).get_metadata_identity(instance_ip, key_file, user, v1)

def _get_security_groups(session: Session):
    console.log("Running `get-security-groups` command.. ([blink purple]OK[/blink purple])")
    Ec2(session, console).get_security_groups()

def _whoami(session: Session):
    console.log("Running `whoami` command.. ([blink purple]OK[/blink purple])")
    ident = Sts(session).whoami()
    keys = ["UserId", "Account", "Arn"]
    values = ident.values()
    ident_tbl = tabulate(zip(keys, values), headers=["Key", "Value"], tablefmt=tbl_fmt)
    console.print(ident_tbl)


# *********************************
# *********** COMMANDS ************
# *********************************

@app.command()
def user_data_rev_shell(
        rhost: str = Argument(..., help="The remote attacker's IP address"),
        rport: int=Option(7777, help="The remote attacker's listening port"),
        instance_type=Option("t2.micro", help="Ec2 instance type"),
        profile: str = Argument(..., help="AWS profile")
    ):
    """
    Obtain a reverse shell via user-data script
    """
    sess = _create_session(profile)
    _user_data_rev_shell(sess)

@app.command()
def launch_ec2_with_instance_profile(
        instance_profile_arn: str = Argument(..., help="Instance profile ARN"),
        ami_id: str = Option("ami-00a208c7cdba991ea", help="The ID of the AMI"),
        key_name: str = Option("awsred-ssh", help="Name of the key pair to create"),
        instance_type: str = Option("t2.micro", help="The instance type to create"),
        subnet_id: str = Option("", help="The subnet ID to launch the Ec2 in"),
        security_group_ids: Optional[List[str]] = Option(None, help="The security group ID's to attach to the new instance"), 
        profile: str = Argument(..., help="AWS profile")
    ):
    """
    Launch an Ec2 instance and attach specified instance profile
    """
    sess = _create_session(profile)
    _launch_ec2_with_instance_profile(
        sess, key_name, ami_id, instance_profile_arn,
        security_group_ids, subnet_id, instance_type
    )

@app.command()
def get_instance_profiles(profile: str = Argument(..., help="AWS profile")):
    """
    List all instance profiles
    """
    sess = _create_session(profile)
    _get_instance_profiles(sess)

@app.command()
def list_permissions(profile: str = Argument(..., help="AWS profile")):
    """
    List permissions associated with profile
    """
    sess = _create_session(profile)
    _list_permissions(sess)

@app.command()
def list_buckets(profile: str = Argument(...,help="AWS profile")):
    """
    List all S3 buckets if allowed
    """
    sess = _create_session(profile)
    _list_buckets(sess)

@app.command()
def dump_buckets(
        bucket: str = Option("", help="Speicific S3 bucket to dump"),
        profile: str = Argument(..., help="AWS profile"),
    ):
    """
    Dump content for all S3 buckets
    """
    sess = _create_session(profile)
    _dump_buckets(sess, bucket)

@app.command()
def add_user_to_group(
        username: str = Argument(..., help="The name of user to create and add to group"),
        password: str = Argument(..., help="The password for the new user"),
        profile: str = Argument(..., help="AWS profile")
    ):
    """
    Attempt to add user to group to escalate privileges
    """
    sess = _create_session(profile)
    _add_user_to_group(sess, username)

@app.command()
def get_instance_creds(
        instance_ip: str = Argument(..., help="IP address of Ec2 instance"),
        key_file: str = Argument(..., help="SSH key file for Ec2 instance"),
        user: str = Argument("ec2-user", help="The SSH user associated with key file"),
        v1: bool=Option(False, help="Use IMDS V1 to get credentials"),
        profile: str = Argument(..., help="AWS profile")
    ):
    """
    Get instance credentials via IMDS (V1|V2)
    """
    sess = _create_session(profile)
    _get_instance_creds(sess, instance_ip, key_file, v1)

@app.command()
def get_user_data(
    instance_ip: str = Argument(..., help="IP address of Ec2 instance"),
    key_file: str = Argument(..., help="SSH key file for Ec2 instance"),
    user: str = Argument(..., help="The SSH user associated with key file"),
    profile: str = Argument(..., help="AWS profile")
    ):
    """
    Get an instances user-data script
    """

@app.command()
def mount_snapshot(
    az: str = Argument(..., help="The availability zone to create the volume in"),
    vol_type: str = Argument(..., help="The type of volume to create"),
    snapshot_id: str = Argument(..., help="The snapshot ID from which to create the volume"),
    profile: str = Argument(..., help="AWS profile")
    ):
    """
    Create EBS volume from snapshot and mount to instance
    """

@app.command()
def get_security_groups(
        profile: str = Argument(..., help="AWS profile") 
    ):
    """
    List all Ec2 instances security groups
    """
    sess = _create_session(profile)
    _get_security_groups(sess)

@app.command()
def whoami(profile: str = Argument(..., help="AWS profile")):
    """
    Get profile identity
    """
    sess = _create_session(profile)
    _whoami(sess)

if __name__ == "__main__":
    app()

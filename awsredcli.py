#!/usr/bin/env python3

# third party
from typer import Typer, echo, Argument, Option
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
    console.log("")

def _launch_ec2_instance_profile(
    session: Session, key_name: str, instance_profile_arn: str):
    console.log("Running `launch-ec2-instance-profile` command.. ([blink purple]ATTENTION[/blink purple])")
    Ec2(session, console).launch_ec2_instance_profile(key_name, instance_profile_arn)

def _get_instance_profiles(session: Session):
    console.log("Running `get-instance-profiles` command.. ([blink purple]ATTENTION[/blink purple])")
    instance_profiles = Ec2(session, console).get_instance_profiles()
    instance_profile_tbl = tabulate(instance_profiles, headers=["InstanceID", "InstanceProfileArn"], tablefmt=tbl_fmt)
    console.print(instance_profile_tbl)

def _ls_perms(session: Session):
    console.log("Running `ls-perms` command.. ([blink purple]ATTENTION[/blink purple])")
    policies = Iam(session, console).get_policies()
    policy_tbl = tabulate(policies, headers=["PolicyName", "PolicyARN"], tablefmt=tbl_fmt)
    console.print(policy_tbl)

def _ls_buckets(session: Session):
    console.log("Running `ls-buckets` command.. ([blink purple]ATTENTION[/blink purple])")
    buckets = S3(session, console).ls_buckets()
    bucket_tbl = tabulate(buckets, headers=["BucketName", "CreationDate"], tablefmt=tbl_fmt)
    console.print(bucket_tbl)

def _dump_bucket(session: Session, bucket: str):
    console.log("Running `dump-bucket` command.. ([blink purple]ATTENTION[/blink purple])")
    pass

def _add_user_to_group(session: Session, username: str):
    console.log("Running `add-user-to-group` command.. ([blink purple]ATTENTION[/blink purple])")
    # use list-groups to list groups and have user select group
    # create user and then add to specified group
    pass

def _get_instance_creds(
    session: Session, instance_ip: str, key_file: str, user: str, v1: bool):
    console.log("Running `get-instance-creds` command.. ([blink purple]ATTENTION[/blink purple])")
    Imds(session, console).get_metadata_identity(instance_ip, key_file, user, v1)

def _get_security_groups(session: Session):
    console.log("Running `get-security-groups` command.. ([blink purple]ATTENTION[/blink purple])")
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
        rhost: str=Argument(..., help="The remote attacker's IP address"),
        rport: int=Option(7777, help="The remote attacker's listening port"),
        instance_type=Option("t2.micro", help="Ec2 instance type"),
        profile: str=Argument(..., help="AWS profile")
    ):
    """
    Obtain a reverse shell via user-data script
    """
    sess = _create_session(profile)
    _user_data_rev_shell(sess)

@app.command()
def launch_ec2_instance_profile(
        key_name: str=Option("awsred", help="Key Pair Name"),
        instance_profile_arn: str=Argument(..., help="instance profile arn"),
        profile: str=Argument(..., help="AWS profile")
    ):
    """
    Launch an Ec2 instance and attach specified instance profile
    """
    sess = _create_session(profile)
    _launch_ec2_instance_profile(sess, key_name, instance_profile_arn)

@app.command()
def get_instance_profiles(profile: str=Argument(..., help="AWS profile")):
    """
    List all instance profiles
    """
    sess = _create_session(profile)
    _get_instance_profiles(sess)

@app.command()
def ls_perms(profile: str=Argument(..., help="AWS profile")):
    """
    List profile permissions
    """
    sess = _create_session(profile)
    _ls_perms(sess)

@app.command()
def ls_buckets(profile: str=Argument(...,help="AWS profile")):
    """
    List all S3 buckets if allowed
    """
    sess = _create_session(profile)
    _ls_buckets(sess)

@app.command()
def dump_bucket(profile: str=Argument(..., help="AWS profile")):
    """
    Dump S3 bucket contents
    """
    sess = _create_session(profile)
    _dump_bucket(sess)

@app.command()
def add_user_to_group(
        username: str=Argument(..., help="The name of user to create and add to group"),
        password: str=Argument(..., help="The password for the new user"),
        profile: str=Argument(..., help="AWS profile")
    ):
    """
    Attempt to add user to group to escalate privileges
    """
    sess = _create_session(profile)
    _add_user_to_group(sess, username)

@app.command()
def get_instance_creds(
        instance_ip: str=Argument(..., help="IP address of Ec2 instance"),
        key_file: str=Argument(..., help="SSH key file for Ec2 instance"),
        user: str=Argument("ec2-user", help="The SSH user associated with key file"),
        v1: bool=Option(False, help="Use IMDS V1 to get credentials"),
        profile: str=Argument(..., help="AWS profile")
    ):
    """
    Get instance credentials via IMDS (V1|V2)
    """
    sess = _create_session(profile)
    _get_instance_creds(sess, instance_ip, key_file, v1)

@app.command()
def get_user_data(
    instance_ip: str=Argument(..., help="IP address of Ec2 instance"),
    key_file: str=Argument(..., help="SSH key file for Ec2 instance"),
    user: str=Argument(..., help="The SSH user associated with key file"),
    profile: str=Argument(..., help="AWS profile")
    ):
    """
    Get an instances user-data script
    """

@app.command()
def mount_snapshot(
    az: str=Argument(..., help="The availability zone to create the volume in"),
    vol_type: str=Argument(..., help="The type of volume to create"),
    snapshot_id: str=Argument(..., help="The snapshot ID from which to create the volume"),
    profile: str=Argument(..., help="AWS profile")
    ):
    """
    Create EBS volume from snapshot and mount to instance
    """

@app.command()
def get_security_groups(
        profile: str=Argument(..., help="AWS profile") 
    ):
    """
    List all Ec2 instances security groups
    """
    sess = _create_session(profile)
    _get_security_groups(sess)

@app.command()
def whoami(profile: str=Argument(..., help="AWS profile")):
    """
    Get profile identity
    """
    sess = _create_session(profile)
    _whoami(sess)

if __name__ == "__main__":
    app()

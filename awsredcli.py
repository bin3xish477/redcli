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

def _user_data_rev_shell(session: Session):
    console.log("Ec2::user data exploit")

def _launch_ec2_instance_profile(
    session: Session, key_name: str, instance_profile_arn: str):
    console.log("Running `launch-ec2-instance-profile` command.. ([bold purple]ATTENTION[/bold purple])")
    Ec2(session, console).launch_ec2_instance_profile(key_name, instance_profile_arn)

def _create_admin_user(session: Session):
    console.log("Creating new user and adding to Administrators group")

def _get_instance_profiles(session: Session):
    console.log("Retrieving instance profiles.. ([bold green]OK[/bold green])")
    instance_profiles = Ec2(session, console).get_instance_profiles()
    instance_profile_tbl = tabulate(instance_profiles, headers=["InstanceID", "InstanceProfileArn"], tablefmt=tbl_fmt)
    console.log(instance_profile_tbl)

def _ls_perms(session: Session):
    policies = Iam(session, console).get_policies()
    console.log("Listing permissions attached to profile.. ([bold green]OK[/ bold green])")
    policy_tbl = tabulate(policies, headers=["PolicyName", "PolicyARN"], tablefmt=tbl_fmt)
    console.log(policy_tbl)

def _ls_buckets(session: Session):
    console.log("Attempting to list buckets.. ([purple underline]ATTENTION[/purple underline])")
    buckets = S3(session, console).ls_buckets()
    bucket_tbl = tabulate(buckets, headers=["BucketName", "CreationDate"], tablefmt=tbl_fmt)
    console.print(bucket_tbl)

def _dump_bucket(session: Session, bucket: str):
    console.log("Attempting to dump contents for")
    pass

def _add_user_to_group(session: Session, username: str):
    # use list-groups to list groups and have user select group
    # create user and then add to specified group
    pass

def _get_instance_creds(
    session: Session, instance_ip: str, key_file: str, v1: bool):
    Imds(session, console).get_metadata_identity(instance_ip, )
    console.print()

def _get_security_groups(session: Session):
    Ec2(session, console).get_security_groups()

def _whoami(session: Session):
    console.log("Invoking `get-caller-identity` API.. ([bold green]OK[/ bold green])")
    ident = Sts(session).whoami()
    console.print(ident)


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
        key_file: str=Argument(..., help="SSH pem key file for Ec2 instance"),
        user: str=Argument("ec2-user", help="The SSH user associated with key"),
        v1: bool=Option(False, help="Use IMDS V1 to get credentials"),
        profile: str=Argument(..., help="AWS profile")
    ):
    """
    Get instance credentials via IMDS (V1|V2)
    """
    sess = _create_session(profile)
    _get_instance_creds(sess, instance_ip, key_file, v1)

@app.command()
def get_security_groups(
        profile: str=Argument(..., help="AWS profile") 
    ):
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

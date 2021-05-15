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

app = Typer()
console = Console()
tbl_fmt = "fancy_grid"


# *********************************
# *********** HELPERS *************
# *********************************

def create_session(profile: str):
    try:
        session = Session(profile_name=profile)
    except ProfileNotFound:
        console.print("Profile was not found.. ([red]ERROR[/red])")
        console.print("Try specifying a different profile name.. ([yellow]ACTION[/yellow])")
        exit()
    return session


# *********************************
# ************* MAIN **************
# *********************************

def _user_data_rev_shell(session: Session):
    console.print("Ec2::user data exploit")

def _launch_ec2_instance_profile(session: Session, key_name: str):
    console.print("Running `launch-ec2-instance-profile` command.. ([bold purple]ATTENTION[/bold purple])")
    Ec2(session, console).run_launch_ec2_instance_profile(key_name)

def _create_admin_user(session: Session):
    console.print("Creating new user and adding to Administrators group")

def _get_instance_profiles(session: Session):
    console.print("Retrieving instance profiles.. ([bold green]OK[/bold green])")
    instance_profiles = Ec2(session, console).get_instance_profiles()
    instance_profile_tbl = tabulate(instance_profiles, headers=["InstanceID", "InstanceProfileArn"], tablefmt=tbl_fmt)
    console.print(instance_profile_tbl)

def _list_perms(session: Session):
    policies = Iam(session, console).get_policies()
    console.print("Listing permissions attached to profile.. ([bold green]OK[/ bold green])")
    policy_tbl = tabulate(policies, headers=["PolicyName", "PolicyARN"], tablefmt=tbl_fmt)
    console.print(policy_tbl)

def _whoami(session: Session):
    console.print("Querying `get-caller-identity` API.. ([bold green]OK[/ boldgreen])")
    iden = Sts(session).whoami()
    del iden["ResponseMetadata"]
    console.print(iden)

# *********************************
# *********** COMMANDS ************
# *********************************

@app.command()
def user_data_rev_shell(
        rhost: str=Argument(..., help="The remote attacker's IP address"),
        rport: int=Option(7777, help="The remote attacker's listening port"),
        instance_type=Option("t2.micro", help="Ec2 instance type"),
        profile: str=Argument("default", help="AWS profile name")
    ):
    """
    Obtain a reverse shell via user-data script
    """
    sess = create_session(profile)
    _user_data_rev_shell(sess)

@app.command()
def launch_ec2_instance_profile(
        key_name: str=Option("awspen", help="Key Pair Name"),
        instance_profile_arn: str=Argument(..., help="instance profile arn"),
        profile: str=Argument("default", help="AWS profile name"),
    ):
    """
    Launch an Ec2 instance and attach specified instance profile
    """
    sess = create_session(profile)
    _launch_ec2_instance_profile(sess, key_name)

@app.command()
def create_admin_user(
        profile: str=Argument("default", help="AWS profile name")
    ):
    """
    Create new user and add to Administrator group
    """
    sess = create_session(profile)
    _create_admin_user(sess)

@app.command()
def get_instance_profiles(
        profile: str=Argument("default", help="AWS profile name")
    ):
    """
    List all instance profiles
    """
    sess = create_session(profile)
    _get_instance_profiles(sess)

@app.command()
def list_perms(
        profile: str=Argument("default", help="AWS profile name")
    ):
    """
    List the permissions for profile
    """
    sess = create_session(profile)
    _list_perms(sess)

@app.command()
def whoami(
        profile: str=Argument("default", help="AWS profile name")
    ):
    """
    Get profile identity
    """
    sess = create_session(profile)
    _whoami(sess)

if __name__ == "__main__":
    app()
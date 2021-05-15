#!/usr/bin/env python3

# third party
from typer import Typer, echo, Argument
from rich.console import Console
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

def _key_pair_launch_ec2(session: Session):
    console.print("Ec2::user data exploit")

def _create_admin_user(session: Session):
    console.print("Creating new user and adding to Administrators group")

def _list_perms(session: Session):
    console.print("Listing permissions attached to profile.. ([red]OK[/red])")

def _whoami(session: Session):
    iden = Sts(session).whoami()
    del iden["ResponseMetadata"]
    console.print(iden)

# *********************************
# *********** COMMANDS ************
# *********************************

@app.command()
def user_data_rev_shell(
        listener_ip: str=Argument(..., help="The remote attacker's IP address"),
        listener_port: int=Argument(..., help="The remote attacker's listening port"),
        profile: str=Argument("default", help="AWS profile name")
    ):
    """
    Obtain a reverse shell via user-data script
    """
    sess = create_session(profile)
    _user_data_rev_shell(sess)

@app.command()
def key_pair_launch_ec2(
        profile: str=Argument("default", help="AWS profile name")
    ):
    """
    Creates SSH key pair and launch an Ec2 instance with the created key pair
    """
    sess = create_session(profile)
    _key_pair_launch_ec2(profile)

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

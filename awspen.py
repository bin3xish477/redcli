#!/usr/bin/env python3

from typer import Typer, echo, Argument
from rich.console import Console
from boto3.session import Session

app = Typer()
console = Console()

def _user_data_rev_shell(profile: str):
    console.print("Ec2::user data exploit")

def _key_pair_launch_ec2(profile: str):
    console.print("Ec2::user data exploit")

def _check(profile: str):
    console.print("[red]Checking permissions[/red]")


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
    Obtain a reverse shell by launching an Ec2 instance with a malicious user-data script
    """
    session = Session(profile_name=f"{profile}")
    _run(profile)

@app.command()
def key_pair_launch_ec2(
        profile: str=Argument("default", help="AWS profile name")
    ):
    session = Session(profile_name=f"{profile}")
    _run(profile)

@app.command()
def check(
        profile: str=Argument("default", help="AWS profile name")
    ):
    session = Session(profile_name=f"{profile}")
    _check(profile)

if __name__ == "__main__":
    app()

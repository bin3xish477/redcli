"""
File: imds.py
Description: contains revelant Azure VM Instance Metadata functions and actions
"""

from paramiko import SSHClient, RSAKey, AutoAddPolicy

class AzImds():

  def __init__(self) -> None:
      pass
  
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

  def get_instance_access_token(self, os: str):
    if os == "nix":
      _, stdout, _ = self.ssh.exec_command(
        "TOKEN=$(curl 'http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https%3A%2F%2Fmanagement.azure.com%2F'"\
        " -H Metadata:true -s) && echo $TOKEN"
      )
    elif os == "win":
      _, stdout, _ = self.ssh.exec_command("""
        Invoke-WebRequest -Uri 'http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https%3A%2F%2Fmanagement.azure.com%2F'\
        -Headers @{Metadata="true"}
        """
      )
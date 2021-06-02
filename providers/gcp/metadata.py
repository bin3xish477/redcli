"""
File: metadata.py
Description: contains revelant GCP Instance Metadata functions and actions
"""
from paramiko import SSHClient, RSAKey, AutoAddPolicy
class MetaData():

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
  # [END _create_ssh_session

  # [START get_instance_token]
  def get_instance_token(self, instance_ip: str, key_file: str, user: str) -> None:
    self._create_ssh_session(instance_ip, key_file, user)
        
    # get instance credentials
    _, stdout, _ = self.ssh.exec_command(
      "curl -s http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token -H 'Metadata-Flavor: Google'"
    )
  # [END get_instance_token]
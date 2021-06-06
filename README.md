# redcli
`redcli` is a cloud penetration testing tool that currently contains some
commands related to AWS pentesting, however, I have already started developing v2 which will also include GCP and Azure penetration testing
operations.

### AWS Help Menu
```bash
% python redcli.py aws --help          


 ██▀███  ▓█████ ▓█████▄  ▄████▄   ██▓     ██▓
▓██ ▒ ██▒▓█   ▀ ▒██▀ ██▌▒██▀ ▀█  ▓██▒    ▓██▒
▓██ ░▄█ ▒▒███   ░██   █▌▒▓█    ▄ ▒██░    ▒██▒
▒██▀▀█▄  ▒▓█  ▄ ░▓█▄   ▌▒▓▓▄ ▄██▒▒██░    ░██░
░██▓ ▒██▒░▒████▒░▒████▓ ▒ ▓███▀ ░░██████▒░██░
░ ▒▓ ░▒▓░░░ ▒░ ░ ▒▒▓  ▒ ░ ░▒ ▒  ░░ ▒░▓  ░░▓  
  ░▒ ░ ▒░ ░ ░  ░ ░ ▒  ▒   ░  ▒   ░ ░ ▒  ░ ▒ ░
  ░░   ░    ░    ░ ░  ░ ░          ░ ░    ▒ ░
   ░        ░  ░   ░    ░ ░          ░  ░ ░  
                 ░      ░
                          Author:  binexisHATT
                          Version: 1.0

Usage: redcli.py aws [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  check-mfa                       Check if MFA is enabled for the...
  dump-buckets                    Dump content for all S3 buckets
  get-instance-access-token       Get instance credentials via Instance...
  get-instance-profiles           List all instance profiles
  get-security-groups             List all Ec2 instances security groups
  get-user-data                   Get an instances user-data script
  launch-ec2-with-instance-profile
                                  Launch an Ec2 instance and attach...
  list-buckets                    List all S3 buckets if allowed
  list-iam-permissions            List permissions associated with profile
  list-s3-acls                    List all S3 bucket Access Control Lists...
  user-data-rev-shell             Obtain a reverse shell via user-data...
  whoami                          Get IAM identity associated with tokens
```


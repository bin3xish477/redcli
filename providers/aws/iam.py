"""
File: iam.py
Description: contains revelant AWS IAM functions and actions
"""

class Iam():

    def __init__(self, session, console) -> None:
        self.iam = session.client("iam")
        self.console = console
        self.admin_policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"

  # [START get_policies]
    def get_policies(self) -> list:
        policy_name = []
        policy_arns = []
        for user_perm in self.iam.get_account_authorization_details(Filter=["User"])["UserDetailList"]:
            for policy in user_perm["AttachedManagedPolicies"]:
                policy_name.append(policy["PolicyName"])
                policy_arns.append(policy["PolicyArn"])
        return list(zip(policy_name, policy_arns))
  # [END get_policies]
    
  # [START create_user]
    def create_user(self) -> None:
        pass
  # [END create_user]

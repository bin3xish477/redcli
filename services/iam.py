
class Iam():

    def __init__(self, session):
        self.session = session
        self.iam = self.session.resource("iam")
        self.admin_policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"

    def __list_perms(self):
        policy_name = []
        policy_arns = []
        for user_perm in self.iam.get_account_authorization_details(Filter=["user"])["UserDetailList"]:
            for policy in user_perm["AttachedManagedPolicies"]:
                policy_name.append(policy["PolicyName"])
                policy_arns.append(policy["PolicyArn"])
        return list(zip(policy_name, policy_arns))
            

"""
File: s3.py
Description: contains revelant AWS S3 functions and actions
"""

from tabulate import tabulate

class S3():

    def __init__(self, session, console) -> None:
        self.s3 = session.client("s3")
        self.s3_resource = session.resource("s3")
        self.console = console

    # [START _list_buckets]
    def _list_buckets(self) -> list:
        bucket_names = []
        creation_dates = []
        buckets = self.s3.list_buckets()
        del buckets["ResponseMetadata"]
        for bucket in buckets["Buckets"]:
            bucket_names.append(bucket["Name"])
            creation_dates.append(str(bucket["CreationDate"]))
        return list(zip(bucket_names, creation_dates))
    # [END _list_buckets]

    # [START dump_buckets]
    def dump_buckets(self, bucket: str) -> None:
        def get_content(bucket: str):
            self.console.print(f"Bucket::[red]{bucket}[/red]")
            objects = self.s3_resource.Bucket(bucket).objects.all() 
            if not objects:
                self.console.print("> No content in this S3 bucket.. ([yellow]INFO[/yellow])")
                return
            self.console.print("[underline]Contents[/underline]")
            for obj in objects:
                self.console.print(' '*2, "\u2022", f"\"{obj.key}\"")
        if not bucket:
            buckets = self._list_buckets()
            for bucket in buckets:
                get_content(bucket[0])
                self.console.print('>'*50, '\n')
        else:
            get_content(bucket)
    # [END dump_buckets]

    # [START list_acls]
    def list_acls(self, bucket: str) -> None:
        """
        TODO: list acls for specific bucket
        """
        buckets = self._list_buckets()
        self.console.print("[green]ACLs[/green]")
        self.console.print("*"*72)
        for bucket in buckets:
            bucket = bucket[0]
            acl = self.s3.get_bucket_acl(
                Bucket=bucket
            )
            self.console.print("[red]Owner[/red]:", acl["Owner"]["DisplayName"])
            for grant in acl["Grants"]:
                grantee = grant["Grantee"]["DisplayName"]
                permissions = grant["Permission"]
                self.console.print(' '*2, f"[magenta]Grantees[/magenta]: {grantee}")
                self.console.print(' '*4, f"[green]Permission[/green]: {permissions}\n")
    # [END list_acls]
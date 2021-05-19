
class S3():

    def __init__(self, session, console):
        self.s3 = session.client("s3")
        self.s3_resource = session.resource("s3")
        self.console = console

    def list_buckets(self):
        bucket_names = []
        creation_dates = []
        buckets = self.s3.list_buckets()
        del buckets["ResponseMetadata"]
        for bucket in buckets["Buckets"]:
            bucket_names.append(bucket["Name"])
            creation_dates.append(str(bucket["CreationDate"]))
        return list(zip(bucket_names, creation_dates))

    def dump_buckets(self, bucket: str):
        def get_content(bucket: str):
            self.console.print(f"Bucket::[red]{bucket}[/red]")
            objects = self.s3_resource.Bucket(bucket).objects.all() 
            if not objects:
                self.console.print("No content in this S3 bucket.. ([yellow]INFO[/yellow])")
                return
            self.console.print("[underline]Contents[/underline]")
            for obj in objects:
                self.console.print(" "*3, "\u2022", f"\"{obj.key}\"")
        if not bucket:
            buckets = self.list_buckets()
            for bucket in buckets:
                get_content(bucket[0])
                self.console.print("\n", ">"*50, "\n")
        else:
            get_content(bucket)


class S3():

    def __init__(self, session, console):
        self.s3 = session.client("s3")
        self.console = console

    def ls_buckets(self):
        buckets = self.s3.list_buckets()
        print(buckets)

    def dump_bucket(self, bucket, all=False):
        pass

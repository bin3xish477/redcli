
class S3():

    def __init__(self, session, console):
        self.s3 = session.client("s3")
        self.console = console

    def ls_buckets(self):
        bucket_names = []
        creation_dates = []
        buckets = self.s3.list_buckets()
        del buckets["ResponseMetadata"]
        for bucket in buckets["Buckets"]:
            bucket_names.append(bucket["Name"])
            creation_dates.append(str(bucket["CreationDate"]))
        return list(zip(bucket_names, creation_dates))

    def dump_bucket(self, bucket: str, all: bool=False):
        pass

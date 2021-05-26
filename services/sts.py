
class Sts():

    def __init__(self, session):
        self.client = session.client("sts")
    
    # [START whoami]
    def whoami(self):
        ident = self.client.get_caller_identity()
        del ident["ResponseMetadata"]
        return ident
    # [END whoami]


class Sts():

    def __init__(self, session):
        self.client = session.client("sts")
    
    def whoami(self):
        return self.client.get_caller_identity()
        

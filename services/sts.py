
class Sts():

    def __init__(self, session):
        self.session = session
    
    def __get_identity(self):
        self.identity = self.session.get_caller_identity()
        return self.identity()
        

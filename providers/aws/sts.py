"""
File: sts.py
Description: contains revelant AWS STS functions and actions
"""

class Sts():

    def __init__(self, session) -> None:
        self.client = session.client("sts")
    
    # [START whoami]
    def whoami(self) -> dict:
        ident = self.client.get_caller_identity()
        del ident["ResponseMetadata"]
        return ident
    # [END whoami]

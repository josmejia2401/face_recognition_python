#from https://dbader.org/blog/records-structs-and-data-transfer-objects-in-python
class SubscriberDTO:

    def __init__(self, data_json = {}, subscribed = False, sessions = []):
        self.username = data_json["username"]
        self.sessions = sessions
        self.subscribed = subscribed
    
    def set_subscribed(self, subscribed = True):
        self.subscribed = subscribed

    def get_subscribed(self):
        return self.subscribed
        
    def add_session(self, session):
        self.sessions.append(session)
    
    def get_sessions(self):
        return self.sessions

    
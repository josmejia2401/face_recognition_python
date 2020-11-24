#from https://dbader.org/blog/records-structs-and-data-transfer-objects-in-python
class UserDTO:

    def __init__(self, data_json = {}):
        self.username = data_json["username"]
        self.password = data_json["password"]
        self.sessions = []
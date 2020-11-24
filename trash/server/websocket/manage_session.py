from server.websocket.dto.dto import UserDTO

class ManageSession:
 
    def __init__(self):
        super().__init__()
        self.__USERS_ONLINE = []
        self.__MAX_SESSIONS = 3
    
    def add_username(self, data: UserDTO = None, session = None) -> UserDTO:
        user_find = self.__check_username(data)
        if user_find is None:
            user_find = self.__add_username(data)
        else:
            user_find = self.__add_session(user_find, session)
        return user_find
        
    def remove_username(self, data: UserDTO = None, session = None) -> UserDTO:
        user_find = self.__check_username(data)
        if user_find is None:
            raise Exception("user does not exist")
        else:
            self.__USERS_ONLINE.remove(user_find)
        return user_find
    
    def get_length_users(self) -> int:
        return len(self.__USERS_ONLINE)

    def get_users(self):
        return self.__USERS_ONLINE

    def __validate_credentials(self, data: UserDTO = None, session = None) -> bool:
        if data.username == data.password:
            return True
        return False

    def __check_username(self, data: UserDTO = None):
        for user in self.__USERS_ONLINE:
            if user.username == data.username:
                return user
        return None
    
    def __add_username(self, data: UserDTO = None, session = None):
        if len(self.__USERS_ONLINE) > self.__MAX_SESSIONS:
            raise Exception("limit exceeded")
        if self.__validate_credentials(data) == False:
            raise Exception("user not valid")
        
        data = self.__add_session(data, session)
        self.__USERS_ONLINE.append(data)
        return data
    
    def __add_session(self, data: UserDTO = None, session = None):
        if session:
            data.sessions.append(session)
        return data
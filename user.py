class User:
    def __init__(self, name, lastname, user_id = -1):
        self.__userid = user_id
        self.__name = name
        self.__lastname = lastname

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def lastname(self):
        return self.__lastname

    @lastname.setter
    def lastname(self, lastname):
        self.__lastname = lastname

    @property
    def userid(self):
        return self.__userid

if __name__ == '__main__':
    user = User("Volker", "Wengert")
    print(user.userid, user.name, user.lastname)
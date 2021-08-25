from Network_Project.user import User
import pickle


class UserMap:
    def __init__(self):
        self.__users = {}

    def add_user(self, user: User):
        self.__users[user.get_ip()] = user

    def get_user(self, ip) -> User:
        try:
            return self.__users[ip]
        except KeyError:
            return None

    def save_user_map(self):
        with open('./saved_users.pkl', 'wb') as saved_users:
            pickle.dump(self.__users, saved_users)

    def load_user_map(self):
        with open('./saved_users.pkl', 'rb') as saved_users:
            self.__users = pickle.load(saved_users)



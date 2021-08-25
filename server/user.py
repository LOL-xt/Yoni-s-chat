from Network_Project.server.db import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(), unique=True, nullable=False)
    nickname = db.Column(db.String(12), nullable=False)
    password = db.Column(db.String(), nullable=False)

    def __init__(self, ip, nickname, password):
        self.ip = ip
        self.nickname = nickname
        self.password = password

    def get_ip(self):
        return self.ip

    def set_ip(self, ip):
        self.ip = ip

    def get_password(self):
        return self.password

    def set_password(self, new_password):
        self.password = new_password

    def get_nickname(self):
        return self.nickname

    def set_nickname(self, new_nickname):
        self.nickname = new_nickname

    def serialize(self):
        return {
            'id': self.id,
            'ip': self.ip,
            'nickname': self.nickname,
            'password': self.password
        }

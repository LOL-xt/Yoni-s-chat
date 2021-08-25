from Network_Project.server.db import db


class User_Group(db.Model):
    __tablename__ = 'users_groups'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), nullable=False)
    group_id = db.Column(db.Integer(), nullable=False)
    is_admin = db.Column(db.Boolean(), nullable=False)
    last_entered = db.Column(db.String(), nullable=True)

    def __init__(self, user_id, group_id, is_admin = False):
        self.user_id = user_id
        self.group_id = group_id
        self.is_admin = is_admin
        self.last_entered = None

    def get_user_id(self):
        return self.user_id

    def set_user_id(self, new_user_id):
        self.user_id = new_user_id

    def get_last_entered(self):
        return self.last_entered

    def set_last_entered(self, new_last_entered):
        self.last_entered = new_last_entered

    def get_group_id(self):
        return self.group_id

    def set_user_id(self, new_group_id):
        self.group_id = new_group_id

    def get_is_admin(self):
        return self.is_admin

    def set_is_admin(self, new_is_admin):
        self.is_admin = new_is_admin

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "group_id": self.group_id,
            "is_admin": self.is_admin,
            "last_entered": self.last_entered
        }
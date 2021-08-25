from datetime import datetime

from Network_Project.server.db import db


class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    last_message_date = db.Column(db.String(), nullable=True)

    def __init__(self, name):
        self.name = name
        self.last_message_date = str(datetime.now())

    def get_name(self):
        return self.name

    def set_nickname(self, new_name):
        self.name = new_name

    def get_last_message_date(self):
        return self.last_message_date

    def set_last_message_date(self, new_date):
        self.last_message_date = new_date

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "last_message_date": self.last_message_date
        }


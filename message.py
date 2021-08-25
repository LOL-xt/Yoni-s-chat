from Network_Project.server.db import db


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.String(), nullable=False)
    date = db.Column(db.String(), nullable=False)
    content = db.Column(db.String(), nullable=False)
    group_id = db.Column(db.Integer(), nullable=False)
    sender_name = db.Column(db.String(), nullable=False)

    def __init__(self, sender_id, sender_name, date, content, group_id):
        self.sender_id = sender_id
        self.date = date
        self.content = content
        self.group_id = group_id
        self.sender_name = sender_name

    def get_sender_id(self):
        return self.sender_id

    def get_sender_name(self):
        return self.sender_name

    def get_date(self):
        return self.date

    def get_content(self):
        return self.content

    def get_group_id(self):
        return self.group_id

    def set_sender_id(self, new_sender_id):
        self.sender_id = new_sender_id

    def set_sender_name(self, new_sender_name):
        self.sender_name = new_sender_name

    def set_date(self, new_date):
        self.date = new_date

    def set_content(self, new_content):
        self.content = new_content

    def set_group_id(self, new_group_id):
        self.group_id = new_group_id

    def serialize(self):
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "date": self.date,
            "content": self.content,
            "group_id": self.group_id,
            "sender_name": self.sender_name
        }

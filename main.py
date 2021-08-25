from datetime import datetime
from sqlalchemy import desc
from flask import Response
from flask import request
from flask import json
from .message import Message
from .user import User
from .group import Group
from .user_group import User_Group
from typing import List
from .db import db, app
from flask_socketio import SocketIO


MIN_CHARACTERS = 5
MAX_CHARACTERS = 17
socketio = SocketIO(app, cors_allowed_origins="*")


@socketio.on('connect', namespace='/group/')
def connect():
    print(f"connected")


@socketio.on('send message')
def handle_send_message(message):
    print("im using it")
    socketio.emit('update message', message)


@socketio.on('update')
def handle_update_user(user):
    socketio.emit('update user', user)


@app.route("/groups/<group_id>")
def get_all_group_messages(group_id):
    current_user_id = request.args.get('user_id')
    update_last_entry(current_user_id, group_id)
    messages: List[Message] = db.session.query(Message).filter(Message.group_id == group_id).all()
    users: List[(User, User_Group)] = db.session.query(User, User_Group.is_admin).join(User_Group, User.id == User_Group.user_id).filter(User_Group.group_id == group_id).all()
    res = {"messages": [], "users": []}
    for e in messages:
        res["messages"].append(e.serialize())
    for e in users:
        user_dict = {}
        user_dict["id"] = e[0].serialize()["id"]
        user_dict["nickname"] = e[0].serialize()["nickname"]
        user_dict["is_admin"] = e[1]
        res["users"].append(user_dict)
    return res


@app.post("/messages")
def add_message():
    data = request.json
    return write_message_to_db(data["sender_id"], data['sender_name'], data['date'], data['content'], data['group_id'])


@app.post("/auth")
def login():
    data = request.json
    current_nickname = data["nickname"]
    current_password = data["password"]
    try:
        user = db.session.query(User).filter(User.nickname == current_nickname).one()
        if current_password == user.password:
            current_user_data = {"user": json.dumps(user.serialize()), "groups": json.dumps(get_user_groups(user.id))}
            return current_user_data
        return Response('Wrong username or password', status=401, mimetype='application/json')
    except Exception as e:
        return Response('Wrong username or password', status=401, mimetype='application/json')


@app.post("/users")
def add_user():
    data = request.json
    current_nickname = data["nickname"]
    current_password = data["password"]
    confirm_password = data["confirm_password"]
    if (MIN_CHARACTERS <= len(current_nickname) <= MAX_CHARACTERS) and len(current_password) >= MIN_CHARACTERS:
        try:
            user = db.session.query(User).filter(User.nickname == current_nickname).one()
            return Response('Nickname is already taken', status=401, mimetype='application/json')
        except Exception as e:
            if current_password == confirm_password:
                new_user = User(data["ip"], current_nickname, current_password)
                db.session.add(new_user)
                db.session.commit()
                return {"user": json.dumps(new_user.serialize())}
            else:
                return Response("Passwords don't match", status=401, mimetype='application/json')
    else:
        if len(current_nickname) < MIN_CHARACTERS or len(current_password) < MIN_CHARACTERS:
            return Response("Nickname and Password must be at least " + str(MIN_CHARACTERS) + " characters long", status=401, mimetype='application/json')
        elif len(current_nickname) > MAX_CHARACTERS:
            return Response("Nickname can't be more than " + str(MAX_CHARACTERS) + " characters long", status=401, mimetype='application/json')


@app.route("/users")
def get_all_users():
    try:
        users: List[User] = User.query.all()
        res = {"users": []}
        for e in users:
           res["users"].append(e.serialize())
        return res
    except Exception as e:
        return (str(e))


@app.post("/groups")
def create_group():
    data = request.json
    # add group to db
    group_name = data["name"]
    if len(group_name) > 0:
        new_group = Group(group_name)
        db.session.add(new_group)
        db.session.commit()
        # add user_group to db
        manager_id = data["manager_id"]
        db.session.refresh(new_group)
        new_user_group = User_Group(manager_id, new_group.id, True)
        db.session.add(new_user_group)
        db.session.commit()
        update_last_entry(manager_id, new_group.id)
        write_message_to_db(37, 'chat admin', str(datetime.now()), f"New Room", new_group.id)
        return {"group": json.dumps({**new_group.serialize(), "last_entered": None})}
    else:
        return Response('Room name must be at least 1 character long', status=400, mimetype='application/json')


@app.route("/users/<user_id>/groups")
def get_groups(user_id):
    try:
        return {"groups": json.dumps(get_user_groups(user_id))}
    except Exception as e:
        return str(e)


@app.post("/groups/<group_id>/users")
def add_user_to_group(group_id):
    data = request.json
    user_to_add_name = data["user_nickname"]
    try:
        user_to_add = db.session.query(User).filter(User.nickname == user_to_add_name).one()
        user_to_add_id = user_to_add.serialize()["id"]
    except:
        return Response('No such user', status=400, mimetype='application/json')
    current_user_group = db.session.query(User_Group).filter(User_Group.group_id == group_id, User_Group.user_id == data["client_id"]).one()
    is_admin = current_user_group.serialize()["is_admin"]
    if is_admin:
        try:
            is_in_group = db.session.query(User_Group).filter(User_Group.user_id == user_to_add_id, User_Group.group_id == group_id).one()
            return Response('User is already in the room', status=400, mimetype='application/json')
        except:
            new_user_group = User_Group(user_to_add_id, group_id, False)
            db.session.add(new_user_group)
            db.session.commit()
            group_notify(user_to_add_id, group_id, "add")
            user_notify(group_id)
            write_message_to_db(37, 'chat admin', str(datetime.now()), f"{user_to_add_name} was added to the room", group_id)
            return {"text": 'Added user successfully', "user": json.dumps(user_to_add.serialize())}
    else:
        return Response('Only room admin can add users', status=400, mimetype='application/json')


@app.route("/groups/<group_id>/users")
def get_all_group_users(group_id):
    users: List[User] = db.session.query(User).join(User_Group, User.id == User_Group.user_id).filter(User_Group.group_id == group_id).all()
    res = {"users": []}
    for e in users:
        res["users"].append(e.serialize())
    return res


@app.post("/groups/<group_id>/users/<user_to_remove_id>/remove")
def remove_user_from_group(group_id, user_to_remove_id):
    data = request.json
    current_user_group = db.session.query(User_Group).filter(User_Group.group_id == group_id, User_Group.user_id == data["client_id"]).one()
    is_admin = current_user_group.serialize()["is_admin"]
    if not int(user_to_remove_id) == data['client_id']:
        if is_admin:
            try:
                user_to_remove: (User_Group, User) = db.session.query(User_Group, User).join(User, User_Group.user_id == User.id).filter(User_Group.group_id == group_id, User_Group.user_id == user_to_remove_id).one()
                if user_to_remove[0].is_admin:
                    return Response('you cant remove admin', status=400, mimetype='application/json')
                db.session.delete(user_to_remove[0])
                db.session.commit()
                group_notify(user_to_remove_id, group_id, "remove")
                user_notify(group_id)
                write_message_to_db(37, 'chat admin', str(datetime.now()), f"{user_to_remove[1].nickname} was removed from the room", group_id)
                return {"text":'Removed User successfuly', "user_id": user_to_remove_id}
            except Exception as e:
                print(e)
                return Response('Choose Participant first', status=400, mimetype='application/json')
        else:
            return Response('Only room admin can remove participants', status=400, mimetype='application/json')
    else:
        return Response('Try the exit button', status=400, mimetype='application/json')


@app.post("/groups/<group_id>/users/<user_to_admin_id>/make_admin")
def make_user_admin(group_id, user_to_admin_id):
    data = request.json
    current_user_group = db.session.query(User_Group).filter(User_Group.group_id == group_id, User_Group.user_id == data["client_id"]).one()
    is_admin = current_user_group.serialize()["is_admin"]
    if is_admin:
        try:
            user_to_admin = db.session.query(User).filter(User.id == user_to_admin_id).one()
            update_admin(user_to_admin_id, group_id)
            user_notify(group_id)
            write_message_to_db(37, 'chat admin', str(datetime.now()), f"{user_to_admin.nickname} is an admin now", group_id)
            return Response('Participant is now admin', status=200, mimetype='application/json')
        except:
            return Response('Choose Participant first', status=400, mimetype='application/json')
    else:
        return Response('This is an admin privilege', status=400, mimetype='application/json')


@app.post("/groups/<group_id>/users/<user_to_admin_id>/make_admin_default")
def make_user_admin_default(group_id, user_to_admin_id):
    try:
        user_to_admin = db.session.query(User).filter(User.id == user_to_admin_id).one()
        update_admin(user_to_admin_id, group_id)
        user_notify(group_id)
        write_message_to_db(37, 'chat admin', str(datetime.now()), f"{user_to_admin.nickname} is an admin now", group_id)
        return Response('Participant is now admin', status=200, mimetype='application/json')
    except:
        return Response('Choose Participant first', status=400, mimetype='application/json')


@app.post("/users/<user_id>/groups/<group_id>/exit")
def exit_group(user_id, group_id):
    has_one_admin = False
    try:
        current_user: List[(User_Group, User)] = db.session.query(User_Group, User).join(User, User_Group.user_id == User.id).filter(User_Group.group_id == group_id, User_Group.user_id == user_id).one()
        write_message_to_db(37, 'chat admin', str(datetime.now()), f"{current_user[1].nickname} left the room", group_id)
        db.session.delete(current_user[0])
        db.session.commit()
        group_notify(user_id, group_id, "remove")
        user_notify(group_id)
        try:
            users: List[(User, User_Group)] = db.session.query(User, User_Group).join(User_Group, User.id == User_Group.user_id).filter(User_Group.group_id == group_id).all()
            if len(users) > 0:
                for user in users:
                    if user[1].serialize()["is_admin"]:
                        has_one_admin = True
                if not has_one_admin:
                    update_admin(users[0][0].id, group_id)
                    write_message_to_db(37, 'chat admin', str(datetime.now()), f"{users[0][0].nickname} is an admin now", group_id)
            else:
                all_group_messages: List[Message] = db.session.query(Message).filter(Message.group_id == group_id).all()
                for message in all_group_messages:
                    db.session.delete(message)
                group_to_remove = db.session.query(Group).filter(Group.id == group_id).one()
                db.session.delete(group_to_remove)
                db.session.commit()
        except Exception as e:
            print(e)
        return {"text": 'Removed User successfuly', "user_id": user_id}
    except:
        pass


def is_admin(group_id, user_id):
    current_user_group = db.session.query(User_Group).filter(User_Group.group_id == group_id, User_Group.user_id == user_id).one()
    is_admin = json.dumps(current_user_group.serialize()["is_admin"])
    return is_admin


def get_user_groups(user_id):
    group_array: List[(Group, str)] = db.session.query(Group, User_Group.last_entered).join(User_Group, Group.id == User_Group.group_id).filter(User_Group.user_id == user_id).order_by(desc(Group.last_message_date)).all()
    res = []
    for e in group_array:
        res.append({**e[0].serialize(), 'last_entered': e[1]})
    return res


def message_notify(message):
    message_data = message.serialize()
    socketio.emit("update message", json.dumps(message_data), namespace=f"/group/{json.dumps(message_data['group_id'])}")


def user_notify(group_id):
    socketio.emit("update user", namespace=f"/group/{group_id}")


def group_notify(user_id, group_id, update_type):
    socketio.emit("update groups", (group_id, update_type), namespace=f"/users/{user_id}/groups")


def update_last_entry(current_user_id, group_id):
    current_user_group = db.session.query(User_Group).filter(User_Group.user_id == current_user_id, User_Group.group_id == group_id).update({'last_entered': str(datetime.now())})
    db.session.commit()


def update_admin(current_user_id, group_id):
    current_user_group = db.session.query(User_Group).filter(User_Group.user_id == current_user_id, User_Group.group_id == group_id).update({'is_admin': True})
    db.session.commit()


def write_message_to_db(sender_id, sender_name, date, content, group_id):
    new_message = Message(sender_id, sender_name, date, content, group_id)
    try:
        if len(content) > 0:
            db.session.query(Group).filter(Group.id == group_id).update({'last_message_date': date})
            db.session.add(new_message)
            db.session.commit()
            message_notify(new_message)
            update_last_entry(sender_id, group_id)
            return Response(content, status=200, mimetype='application/json')
        else:
            return Response('Message must contain at least 1 character', status=400, mimetype='application/json')
    except Exception as e:
        print(e)
        return Response("Couldn't send message, choose another room", status=400, mimetype='application/json')


db.create_all()
socketio.run(app)
#app.run(debug=True)





from app.main import db, app, socketio
if __name__ == '__main__':
    app.run()
    db.create_all()
    socketio.run(app)
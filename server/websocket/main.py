#!/usr/bin/env python3
#!/usr/bin/python3.8
# OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from flask_socketio import join_room, leave_room, send, emit, disconnect
import functools

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")
USERS_ONLINE = []
def is_connected(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        try:
            session_id = request.sid 
            global USERS_ONLINE
            r = [i for i in USERS_ONLINE if i == str(session_id)]
            if len(r) > 0:
                return f(*args, **kwargs)
            else:
                on_disconnect()
        except:
            on_disconnect()
    return wrapped

def is_process_frame():
    global USERS_ONLINE
    if len(USERS_ONLINE) > 1:
        return True
    else:
        return False

@socketio.on('on_message')
def handle_message(data):
    send(data, json=True)

@socketio.on('on_frame')
@is_connected
def handle_on_frame(data):
    if is_process_frame():
        emit('evt_frame', data, json=True, broadcast=True)

@socketio.on('connect')
def on_connect():
    print('connected')

@socketio.on('disconnect')
def on_disconnect():
    try:
        disconnect()
        print('disconnected')
    except:
        pass

@socketio.on('on_subscriber')
def on_subscriber():
    try:
        session_id = request.sid 
        global USERS_ONLINE
        r = [i for i in USERS_ONLINE if i == str(session_id)]
        if len(r) > 0:
            handle_message({"message" : "usuario ya existe"})
            on_disconnect()
        elif len(USERS_ONLINE) > 3:
            on_disconnect()
        else:
            USERS_ONLINE.append(str(session_id))
            print('user on_subscriber: ' , str(session_id))
            if is_process_frame():
                emit('on_process_frame', '1', broadcast=True)
            else:
                emit('on_process_frame', '0', broadcast=True)
    except Exception as e:
        print(e)

@socketio.on('on_unsubscriber')
def on_unsubscriber():
    try:
        session_id = request.sid 
        global USERS_ONLINE
        r = [i for i in USERS_ONLINE if i == str(session_id)]
        if len(r) > 0:
            for i in r:
                USERS_ONLINE.remove(i)
            #on_disconnect()
            if is_process_frame():
                emit('on_process_frame', '1', broadcast=True)
            else:
                emit('on_process_frame', '0', broadcast=True)
        else:
            print('user not exist: ' , str(session_id))
    except:
        pass

def run():
    socketio.run(app, host='0.0.0.0', port='5000', debug=True, use_reloader=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port='5000', debug=True, use_reloader=True)
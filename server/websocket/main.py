#!/usr/bin/env python3
#!/usr/bin/python3.8
# OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from flask_socketio import join_room, leave_room, send, emit, disconnect
import functools
from dto.dto import SubscriberDTO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")
USERS_ONLINE = []
def is_connected(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        try:
            if "username" in args[0]:
                username = args[0]["username"]
                session_id = request.sid 
                global USERS_ONLINE
                subscriber_dto = __check_username(USERS_ONLINE, username, session_id)
                if subscriber_dto is None:
                    __disconnect_sid(session_id)
                elif subscriber_dto.get_subscribed() == False:
                    __disconnect_sid(session_id)
                else:
                    return f(*args, **kwargs)
            else:
                on_disconnect()
        except:
            on_disconnect()
    return wrapped

@socketio.on('on_message')
@is_connected
def handle_message(data):
    send(data, json=True)

@socketio.on('on_frame')
@is_connected
def handle_on_frame(data):
    emit('evt_frame', data, json=True, broadcast=True)

@socketio.on('connect')
def on_connect():
    username = request.args.get('username')
    session_id = request.sid 
    if username is None:
        __disconnect_sid(session_id)
    else:
        global USERS_ONLINE
        subscriber_dto = __check_username(USERS_ONLINE, username, session_id)
        if subscriber_dto is None:
            __subscriber_user(USERS_ONLINE, {"username" : username }, session_id)
        else:
            subscriber_dto.add_session(session_id)

@socketio.on('on_subscriber')
def on_subscriber(data_json):
    try:
        session_id = request.sid 
        if "username" in data_json:
            username = data_json["username"]
        elif request.args.get('username'):
            username = request.args.get('username')
        else:
            __disconnect_sid(session_id)
            return
        global USERS_ONLINE
        subscriber_dto = __check_username(USERS_ONLINE, username, session_id)
        if subscriber_dto is None:
            __disconnect_sid(session_id)
        else:
            subscriber_dto.set_subscribed(True)
            subscriber_dto.add_session(session_id)
    except Exception as e:
        print(e)

@socketio.on('disconnect')
def on_disconnect():
    username = request.args.get('username')
    session_id = request.sid 
    if username is None:
        __disconnect_sid(session_id)
    else:
        global USERS_ONLINE
        subscriber_dto = __check_username(USERS_ONLINE, username, session_id)
        if subscriber_dto is None:
            __disconnect_sid(session_id)
        else:
            #__unsubscriber_user(USERS_ONLINE, subscriber_dto, session_id)
            __disconnect_sid(session_id)

@socketio.on('on_unsubscriber')
def on_unsubscriber(data_json = {}):
    try:
        session_id = request.sid 
        if "username" in data_json:
            username = data_json["username"]
        elif request.args.get('username'):
            username = request.args.get('username')
        else:
            __disconnect_sid(session_id)
            return
        global USERS_ONLINE
        subscriber_dto = __check_username(USERS_ONLINE, username, session_id)
        if subscriber_dto is None:
            __disconnect_sid(session_id)
        else:
            __unsubscriber_user(USERS_ONLINE, subscriber_dto, session_id)
    except Exception as e:
        print(e)

def __unsubscriber_user(USERS_ONLINE = [], subscriber_dto: SubscriberDTO = None, session_id = None):
    for s in subscriber_dto.sessions:
        __disconnect_sid(s)
    subscriber_dto.sessions = []
    USERS_ONLINE.remove(subscriber_dto)
    __is_transmit_frame(USERS_ONLINE)
    print('user __unsubscriber_user: ' , subscriber_dto.username)

def __check_username(USERS_ONLINE, username, session_id):
    r = [i for i in USERS_ONLINE if i.username == username]
    if len(r) > 0:
        if isinstance(r[0], SubscriberDTO) == True:
            return r[0]
        else:
            return None
    else:
        return None

def __subscriber_user(USERS_ONLINE, data_json, session_id):
    if len(USERS_ONLINE) > 3:
        __disconnect_sid(session_id)
    else:
        subscriber_dto = SubscriberDTO(data_json=data_json)
        USERS_ONLINE.append(subscriber_dto)
        __is_transmit_frame(USERS_ONLINE)
        print('user on_subscriber: ' , str(data_json))

def __disconnect_sid(sid=None):
    try:
        disconnect(sid)
        print('disconnected', sid)
    except:
        pass

def __is_transmit_frame(USERS_ONLINE):
    if len(USERS_ONLINE) > 1:#comenzar a transmitir
        print("on_transmit_frame", 1)
        emit('on_transmit_frame', "1", json=False, broadcast=True)
    else:
        print("on_transmit_frame", 2)
        emit('on_transmit_frame', "2", json=False, broadcast=True)


def run():
    socketio.run(app, host='0.0.0.0', port='5000', debug=True, use_reloader=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port='5000', debug=True, use_reloader=True)
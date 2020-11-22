#!/usr/bin/env python3
#!/usr/bin/python3.8
# OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
from flask import Flask, request, render_template
from flask_socketio import SocketIO
from flask_socketio import send, emit, disconnect
from dto.dto import UserDTO
from manage_session import ManageSession

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")
manage_session = ManageSession()

@app.route('/')
def start():
    return render_template('index.html')

@socketio.on('connect')
def on_connect():
    session_id = request.sid
    try:
        username = request.args.get('username')
        password = request.args.get('password')
        if username is None or password is None:
            disconnect(session_id)
        else:
            user_json = {"username": username, "password": password}
            user_dto = UserDTO(user_json)
            global manage_session
            user_find = manage_session.add_username(user_dto, session_id)
            length_users = manage_session.get_length_users()
            emit('stream_video', str(length_users), broadcast=True, json=False, include_self=True)
    except KeyError as e:
        disconnect(session_id)
        print(e)
    except Exception as e:
        disconnect(session_id)
        print(e)
    except:
        pass

@socketio.on('subscriber')
def on_subscriber():
    session_id = request.sid
    try:
        username = request.args.get('username')
        password = request.args.get('password')
        if username is None or password is None:
            disconnect(session_id)
        else:
            user_json = {"username": username, "password": password}
            user_dto = UserDTO(user_json)
            global manage_session
            user_find = manage_session.add_username(user_dto, session_id)
            length_users = manage_session.get_length_users()
            emit('stream_video', str(length_users), broadcast=True, json=False, include_self=True)
    except KeyError as e:
        disconnect(session_id)
        print(e)
    except Exception as e:
        disconnect(session_id)
        print(e)
    except:
        pass


@socketio.on('disconnect')
def on_disconnect():
    session_id = request.sid
    try:
        username = request.args.get('username')
        password = request.args.get('password')
        if username is None or password is None:
            disconnect(session_id)
        else:
            disconnect(session_id)
    except Exception as e:
        disconnect(session_id)
        print(e)


@socketio.on('unsubscriber')
def on_unsubscriber():
    session_id = request.sid
    try:
        username = request.args.get('username')
        password = request.args.get('password')
        if username is None or password is None:
            disconnect(session_id)
        else:
            user_json = {"username": username, "password": password}
            user_dto = UserDTO(user_json)
            global manage_session
            user_find = manage_session.remove_username(user_dto, session_id)
            for s in user_find.sessions:
                if s == session_id:
                    continue
                disconnect(s)
            user_find.sessions = []
            length_users = manage_session.get_length_users()
            emit('stream_video', str(length_users), broadcast=True, json=False, include_self=True)
    except KeyError as e:
        disconnect(session_id)
        print(e)
    except Exception as e:
        disconnect(session_id)
        print(e)
    except:
        pass

@socketio.on('cv-data')
def cv_data(data):
    emit('handle-cv-data', data, json=True, broadcast=True)

def run():
    socketio.run(app, host='0.0.0.0', port='5000', debug=True, use_reloader=True)

if __name__ == '__main__':
    run()

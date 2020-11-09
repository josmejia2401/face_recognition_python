#!/usr/bin/env python3
#!/usr/bin/python3.8
# OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_socketio import join_room, leave_room, send, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('on_message')
def handle_message(message):
    send(message, json=True)

@socketio.on('on_frame')
def handle_message(data):
    print("handle_message", data['image'])
    emit('evt_frame', data, json=True, broadcast=True)

@socketio.on('connect')
def on_connect():
    print('connected')

@socketio.on('disconnect')
def on_disconnect():
    print('disconnected')

@socketio.on('join')
def on_join(data):
    print('received join: ' + str(data))

@socketio.on('leave')
def on_leave():
    print('Client leave')

def run():
    socketio.run(app, host='0.0.0.0', port='5000', debug=True, use_reloader=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port='5000', debug=True, use_reloader=True)
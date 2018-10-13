#!/usr/bin/env python
from threading import Lock
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from random import randrange

# Set this variable to "threading", "eventlet" or "gevent" or None
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!yo'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


def background_thread():
    """Example of how to send server generated events to clients."""
    while True:
        color = randrange(255)
        socketio.emit('my_response',
                      {'event': 'newgame', 'color':color},
                      namespace='/test')
        socketio.sleep(3)


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('my_event', namespace='/test')
def test_message(message):
    emit('my_response',
         {'data': message['data']})


@socketio.on('my_broadcast_event', namespace='/test')
def test_broadcast_message(message):
    emit('my_response',
         {'data': message['data']},
         broadcast=True)


@socketio.on('color_pick', namespace='/test')
def change_color(message):
    emit('put_color', {'color': message['color']},
         broadcast=True)

	
@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    emit('my_response',
         {'data': 'Disconnected!'})
    disconnect()

	
@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)
    emit('my_response', {'data': 'Connected'})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=True, host= '0.0.0.0', port=80)

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

colors = ((1,0,0), (0,1,0), (0,0,1), (1,1,0))
player1_progress = 0
player2_progress = 0
player1_score = 0
player2_score = 0
player1 = None
player2 = None


def to_color(color):
    return 'rgb(' + str(color[0] * 255) + ', ' + str(color[1] * 255) + ', ' + str(color[2] * 255) + ')'


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
    global player1
    global player2
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)
        if player1 is None:
            player1 = request.sid
            print('client 1 connected')
        elif player2 is None:
            player2 = request.sid
            print('client 2 connected')
    emit('init', {'color1': to_color(colors[0]), 'color2': to_color(colors[1]), 'color3': to_color(colors[2]), 'color4': to_color(colors[3])})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)
    global player1
    global player2
    if player1 == request.sid:
        player1 = None
        print('client 1 disconnected')
    elif player2 == request.sid:
        player2 = None
        print('client 2 disconnected')


if __name__ == '__main__':
    socketio.run(app, debug=True, host= '0.0.0.0', port=80)

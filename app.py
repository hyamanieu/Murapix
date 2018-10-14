#!/usr/bin/env python
from threading import Lock
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from random import randrange
#from pixdriver import display, init_serial

# Set this variable to "threading", "eventlet" or "gevent" or None
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!yo'

socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

colors = ((0,0,1), (0,1,0), (1,0,0), (0,1,1))
player1_progress = 0
player2_progress = 0
player1_score = 0
player2_score = 0
player1 = None
player2 = None


def to_color(color):
    return 'rgb(' + str(color[0] * 255) + ', ' + str(color[1] * 255) + ', ' + str(color[2] * 255) + ')'
    
    
def from_color(color):
    rgb = color[4:-1].split(',')
    return (1 if rgb[0].strip() == '255' else 0, 1 if rgb[1].strip() == '255' else 0, 1 if rgb[2].strip() == '255' else 0)


def background_thread():
    """Example of how to send server generated events to clients."""
    while True:
        color = randrange(255)
        socketio.emit('my_response',
                      {'event': 'newgame', 'color':color},
                      namespace='/test')
        socketio.sleep(3)
        
@app.before_first_request
def init():
    pass
    #init_serial()

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('color_pick', namespace='/test')
def color_picked(message):
    print('color_pick ')
    print(message)
    global player1_progress
    global player2_progress
    global player1_score
    global player2_score
    if player1 == request.sid:
        if colors[player1_progress] == from_color(message['color']):
            player1_progress += 1
            print('client 1 color ok')
    elif player2 == request.sid:
        if colors[player2_progress] == from_color(message['color']):
            player2_progress += 1
            print('client 1 color ok')
            
    if player1_progress >= 4 or player2_progress >= 4:
        if player1_progress >= 4:
            print('player 1 win')
            player1_score += 1
        else:
            print('player 2 win')
            player2_score += 1
        player1_progress = 0
        player2_progress = 0

    refresh_display()
    #emit('put_color', {'color': message['color']},
    #     broadcast=True)

	
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
    player = 0
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)
        if player1 is None:
            player1 = request.sid
            player = 1
            print('client 1 connected')
        elif player2 is None:
            player2 = request.sid
            player = 2
            print('client 2 connected')
    emit('init', {'color1': to_color(colors[0]), 'color2': to_color(colors[1]), \
        'color3': to_color(colors[2]), 'color4': to_color(colors[3]), 'player': player})


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
    
    
def refresh_display():
    #display(colors, player1_progress, player2_progress, player1_score, player2_score)
    pass
    

if __name__ == '__main__':
    #refresh_display()
    socketio.run(app, debug=True, host= '0.0.0.0', port=80)

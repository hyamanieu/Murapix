#!/usr/bin/env python

"""
start it with:
FLASK_APP=app_sensehat.py flask run --host=0.0.0.0

if you don't have a raspberry pi with a sense hat, you can install
an emulater. See documentation: 
    https://sense-emu.readthedocs.io/en/v1.0/install.html

2 players exactly
"""








from threading import Lock
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from random import randrange
import numpy as np
import os
import time


if os.uname().nodename == "raspberrypi":
    from sense_hat import SenseHat
    israsp = True
    CURR_IM = 'heart.png'
else:
    israsp = False
    from sense_emu import SenseHat


# Set this variable to "threading", "eventlet" or "gevent" or None
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!yo'

socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

#4 colors the game will use, displayed on the client
INIT_COLORS = ((0,0,1), (0,1,0), (1,0,0), (0,1,1))
a0 = np.empty(4,dtype=object)
a0[:] = INIT_COLORS
LEN_TARGET = 8
TARGET_COLORS = np.random.choice(a0,LEN_TARGET)

PLAYER1_PROGRESS = 0
PLAYER2_PROGRESS = 0
PLAYER1_SCORE = 0
PLAYER2_SCORE = 0
player1 = None
player2 = None
NOGO = True# game won't budget as long as start_game is not run


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
    print('######################')
    start_game()
    refresh_display()
    #init_serial()

@app.route('/')
def index():
    
    refresh_display()
    return render_template('index.html', async_mode=socketio.async_mode)



@socketio.on('color_pick', namespace='/test')
def color_picked(message):
    print('color_pick ')
    print(message)
    global PLAYER1_PROGRESS
    global PLAYER2_PROGRESS
    global PLAYER1_SCORE
    global PLAYER2_SCORE
    global TARGET_COLORS
    global NOGO
    
    if NOGO:
        print("Please wait")
        wait_message()
        return
        
    
    if player1 == request.sid:
        if TARGET_COLORS[PLAYER1_PROGRESS] == from_color(message['color']):
            PLAYER1_PROGRESS += 1
            print('client 1 color ok')
    elif player2 == request.sid:
        if TARGET_COLORS[PLAYER2_PROGRESS] == from_color(message['color']):
            PLAYER2_PROGRESS += 1
            print('client 1 color ok')
            
    if PLAYER1_PROGRESS >= LEN_TARGET or PLAYER2_PROGRESS >= LEN_TARGET:
        if PLAYER1_PROGRESS >= LEN_TARGET:
            print('player 1 win')
            PLAYER1_SCORE += 1
            show_winner("1")
        else:
            print('player 2 win')
            PLAYER2_SCORE += 1
            show_winner("2")
            time.sleep(0.5)
        PLAYER1_PROGRESS = 0
        PLAYER2_PROGRESS = 0
        TARGET_COLORS = np.random.choice(a0,LEN_TARGET)
    
    if PLAYER1_SCORE >= 4:
        NOGO = True
        show_winner("W")
        show_winner("1")
        PLAYER1_SCORE=0
        PLAYER2_SCORE=0
        start_game()
    elif  PLAYER2_SCORE>=4:
        NOGO = True
        show_winner("W")
        show_winner("2")
        PLAYER1_SCORE=0
        PLAYER2_SCORE=0
        start_game()
        

        
        
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
        if not player1 or not player2:
            wait_message()
        else:
            start_game()
    emit('init', {'color1': to_color(INIT_COLORS[0]), 'color2': to_color(INIT_COLORS[1]), \
        'color3': to_color(INIT_COLORS[2]), 'color4': to_color(INIT_COLORS[3]), 'player': player})


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
    
    wait_message()

def wait_message():
    global NOGO
    sense = SenseHat()
    sense.show_message('...')
    NOGO = True
    
def refresh_display():
    #display(colors, PLAYER1_PROGRESS, PLAYER2_PROGRESS, PLAYER1_SCORE, PLAYER2_SCORE)
    sense = SenseHat()
    p1 = [255*c for c in TARGET_COLORS[PLAYER1_PROGRESS]]
    p2 = [255*c for c in TARGET_COLORS[PLAYER2_PROGRESS]]
    k = [0, 0, 0]#black pixel
    s1 = [125,78,0]#color of player 1 score
    s2 = [0,78,125]
    
    print(f"""Player 1 current color:{p1}
    Player 2 current color:{p2}
    Player 1 score: {PLAYER1_SCORE}
    Player 2 score: {PLAYER2_SCORE}""")
    
    #set score line
    score_line = [k,k,k,k,k,k,k,k]
    score_line[:PLAYER1_SCORE] = [s1]*PLAYER1_SCORE
    if PLAYER2_SCORE>0:
        score_line[-PLAYER2_SCORE:] = [s2]*PLAYER2_SCORE
    p1_progress_line = [k,k,k,k,k,k,k,k]
    p1_progress_line[:PLAYER1_PROGRESS] = [s1]*PLAYER1_PROGRESS
    p2_progress_line = [k,k,k,k,k,k,k,k]
    p2_progress_line[:PLAYER2_PROGRESS] = [s2]*PLAYER2_PROGRESS
    
    screen= ([p1]*4+[p2]*4
             +[p1]*4+[p2]*4
             +[p1]*4+[p2]*4
             +[p1]*4+[p2]*4
             +p1_progress_line
             +p2_progress_line
             +[k]*8
             +score_line)
    
    
    sense.set_pixels(screen)
    
def show_winner(winner):
    """
    winner should be a single character (string) "1" or "2"
    """
    sense = SenseHat()
    sense.show_letter(winner)
    time.sleep(0.5)
    sense.clear()
    time.sleep(0.5)
    sense.show_letter(winner)
    time.sleep(0.5)
    sense.clear()
    time.sleep(0.5)
    sense.show_letter(winner)
    time.sleep(0.5)
    sense.clear()

def start_game():
    global NOGO
    sense = SenseHat()
    sense.show_letter("3")
    time.sleep(0.5)
    sense.clear()
    time.sleep(0.5)
    sense.show_letter("2")
    time.sleep(0.5)
    sense.clear()
    time.sleep(0.5)
    sense.show_letter("1")
    time.sleep(0.5)
    sense.clear()
    NOGO = False

if __name__ == '__main__':
    refresh_display()
    socketio.run(app, debug=True, host= '0.0.0.0', port=80)

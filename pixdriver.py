from serial import Serial
import time
from random import randrange

line1_pixel_count = 144
line2_pixel_count = 144
line3_pixel_count = 60
max_score = 7
block_count = 4
off_color = (0,0,0)
score_color = (1,0,0)

colors = ((0,0,1), (0,1,0), (1,0,0), (0,1,1))
player1_progress = 0
player2_progress = 0
player1_score = 0
player2_score = 0

global port
port = None


def init_serial():
    global port
    if port is None:
        print("init")
        port = Serial('COM3', 9600, timeout=5)
        time.sleep(3)
        print(port.name)


def display(c, p1p, p2p, p1s, p2s):
    global port
    init_serial()
    
    global colors
    global player1_progress
    global player2_progress
    global player1_score
    global player2_score
    
    colors = c
    player1_progress = p1p
    player2_progress = p2p
    player1_score = p1s
    player2_score = p2s
    
    encoded = led_encode()
    values = bytearray(encoded)
    for b in values:
        c = str.encode(str(b))
        port.write(c)
        time.sleep(0.001)
    port.close()


def led_encode():
    bytes = []
    
    # first line is player 1 current progress
    block_size = int(line1_pixel_count / block_count)
    for block in range(block_count):
        block_color = colors[block] if player1_progress <= block else off_color
        for i in range(block_size):
            bytes.append(block_color)
    
    # second line is player 2 current progress
    block_size = int(line2_pixel_count / block_count)
    # line 2 is addressed in reverse
    for block in reversed(range(block_count)):
        block_color = colors[block] if player2_progress <= block else off_color
        for i in range(block_size):
            bytes.append(block_color)
    
    # third line is players score
    block_size = int(line3_pixel_count / 2)
    score1_size = int(block_size * (player1_score / max_score))
    score2_size = int(block_size * (player2_score / max_score))
    offset = line3_pixel_count - score1_size - score2_size
    for i in range(score1_size):
        bytes.append(score_color)
    for i in range(offset):
        bytes.append(off_color)
    for i in range(score2_size):
        bytes.append(score_color)
    
    # each color is encoded in 4 bits
    # one byte contain 2 colors, encoded on 4 bits, with the last bit being useless
    compressed_bytes = []
    for i in range(0, len(bytes), 2):
        compressed_bytes.append((bytes[i][0]) | (bytes[i][1] << 1) | (bytes[i][2] << 2) \
            | (bytes[i+1][0] << 4) | (bytes[i+1][1] << 5) | (bytes[i+1][2] << 6))
    

    #compressed_bytes = []
    #for byte in bytes:
    #    compressed_bytes.append(((byte[0]) | (byte[1] << 1) | (byte[2] << 2)))
    
    return compressed_bytes

    
def test():
    #port = Serial('COM3', 9600, timeout=5)
    #byte = randrange(255)
    #port.write(6)
    #car = port.readline()
    #print(car)
    #port.close()
    global colors
    global player1_progress
    global player2_progress
    global player1_score
    global player2_score
    print(led_encode())
    player1_progress = 1
    print(led_encode())
    player1_progress = 2
    player2_progress = 1
    print(led_encode())
    player1_progress = 3
    print(led_encode())
    player1_progress = 4
    player2_progress = 2
    player1_score = 1
    print(led_encode())
    
    

def send():
    port = Serial('COM3', 9600, timeout=5)
    print(port.name)
    #time.sleep(4)

    if (port.isOpen()):
        encoded = led_encode()
        print(len(encoded))
        print(encoded)
        values = bytearray(encoded)
        time.sleep(4)
        for b in values:
            c = str.encode(str(b))
            #print(c)
            port.write(c)
            time.sleep(0.001)
        # attend que des données soit revenues
        while(port.inWaiting() == 0):
            # on attend 0.5 seconde pour que les données arrivent
            time.sleep(0.5)

        while(port.inWaiting() != 0):
            car = port.readline()
            #print(car)

        port.close()
    else:
        print ("Le port n'a pas pu être ouvert !")

        
if __name__ == '__main__':
    #send()
    test()
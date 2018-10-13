from serial import Serial
import time

line1_pixel_count = 108
line2_pixel_count = 108
line3_pixel_count = 60
max_score = 7
block_count = 4
off_color = (0,0,0)
score_color = (1,0,0)

colors = ((1,0,0), (0,1,1), (1,0,1), (0,1,1))
player1_progress = 0
player2_progress = 1
player1_score = 3
player2_score = 2

def led_encode():
    bytes = []
    
    # first line is player 1 current progress
    block_size = int(line1_pixel_count / block_count)
    for block in range(block_count):
        block_color = colors[block] if player1_progress < block else off_color
        for i in range(block_size):
            bytes.append(block_color)
    
    # second line is player 2 current progress
    block_size = int(line2_pixel_count / block_count)
    # line 2 is addressed in reverse
    for block in reversed(range(block_count)):
        block_color = colors[block] if player1_progress < block else off_color
        for i in range(block_size):
            bytes.append(block_color)
    
    # third line is players score
    block_size = int(line3_pixel_count / 2)
    score1_size = block_size * int(player1_score / max_score)
    score2_size = block_size * int(player2_score / max_score)
    offset = line3_pixel_count - score1_size - score2_size
    for i in range(score1_size):
        bytes.append(score_color)
    for i in range(offset):
        bytes.append(score_color)
    for i in range(score2_size):
        bytes.append(score_color)
    
    # each color is encoded in 4 bits
    # one byte contain 2 colors, encoded on 4 bits, with the last bit being useless
    compressed_bytes = []
    for i in range(0, len(bytes), 2):
        compressed_bytes.append((bytes[i][0]) & (bytes[i][1] << 1) & (bytes[i][2] << 2) \
            & (bytes[i+1][0] << 4) & (bytes[i+1][1] << 5) & (bytes[i+1][2] << 6))
    
    return compressed_bytes


def send():
    port = Serial('COM3', 9600)
    print(port.name)

    if (port.isOpen()):
        values = bytearray(led_encode())
        port.write(values)
        # attend que des données soit revenues
        while(port.inWaiting() == 0):
            # on attend 0.5 seconde pour que les données arrivent
            time.sleep(0.5)

        #while(port.inWaiting() != 0):
        #    car = port.read()
        #    print(car)

        port.close()
    else:
        print ("Le port n'a pas pu être ouvert !")
